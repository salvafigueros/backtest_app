from .performance import create_sharpe_ratio, create_drawdowns, create_cagr, create_sortino_ratio
from math import floor
from .event.orderEvent import OrderEvent
from ..stock import Stock
from ..futures import Futures
import pandas as pd 
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import math
import datetime

#Chart
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plot
import mpld3
import seaborn as sns
from matplotlib.figure import Figure


class PortfolioBacktesting(object):

    def __init__(self, bars, events, start_date, starting_cash=100000.0, currency="USD"):
        self.bars = bars
        self.events = events
        self.ticker_list = self.bars.ticker_list
        self.start_date = start_date
        self.starting_cash = starting_cash
        self.currency = currency

        #Positions
        self.all_positions = self.construct_all_positions()
        self.current_positions = dict( (k,v) for k, v in [(t, 0) for t in self.ticker_list] )

        #Holdings
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

        self.all_returns = self.construct_all_returns()
        self.latest_positions = dict( (k,v) for k, v in [(t, 0) for t in self.ticker_list] )

        #Operations
        self.all_operations = pd.DataFrame(columns=["timeindex", "asset", "direction", "price", "quantity"])



    def construct_all_positions(self):
        d = dict( (k,v) for k, v in [(t, 0) for t in self.ticker_list] )
        d['datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        d = dict( (k,v) for k, v in [(t, 0.0) for t in self.ticker_list] )
        d['datetime'] = self.start_date
        d['cash'] = self.starting_cash
        d['commission'] = 0.0
        d['total'] = self.starting_cash
        return [d]

    def construct_all_returns(self):
        d = dict( (k,v) for k, v in [(t, 0.0) for t in self.ticker_list] )
        d['datetime'] = self.start_date
        return d


    def construct_current_holdings(self):
        d = dict( (k,v) for k, v in [(t, 0.0) for t in self.ticker_list] )
        d['cash'] = self.starting_cash
        d['commission'] = 0.0
        d['total'] = self.starting_cash
        return d


    @staticmethod
    def get_asset_currency(asset):
        asset = Stock.get_stock_by_ticker(asset)
        if asset == False:
            asset = Futures.get_futures_by_ticker(asset)
            if asset == False:
                return 0
        return asset.currency


    def update_timeindex(self, event):
        bars = {}
        for ticker in self.ticker_list:
            bars[ticker] = self.bars.get_latest_bars(ticker, N=1)

        # Update positions
        dp = dict( (k,v) for k, v in [(t, 0) for t in self.ticker_list] )
        dp['datetime'] = bars[self.ticker_list[0]][0][1]

        for t in self.ticker_list:
            dp[t] = self.current_positions[t]

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        dh = dict( (k,v) for k, v in [(t, 0) for t in self.ticker_list] )
        dh['datetime'] = bars[self.ticker_list[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for t in self.ticker_list:
            # Approximation to the real value
            market_value = 0
            if math.isnan(bars[t][0][5]) == False:
                market_value = self.current_positions[t] * bars[t][0][5]
            dh[t] = market_value
            dh['total'] += market_value 


        # Append the current holdings
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        self.current_positions[fill.ticker] += fill_dir*fill.quantity

    def update_holdings_from_fill(self, fill):
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bars(fill.ticker)[0][5]  # Close price
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.ticker] += cost
        self.current_holdings['commission'] += fill.commission 
        self.current_holdings['cash'] -=  (cost + fill.commission) 
        self.current_holdings['total'] -= (cost + fill.commission) #Incorrecto


    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)


    def generate_order(self, signal):
        order = None

        ticker = signal.ticker
        direction = signal.signal_type

        no_position = sum(1 for v in self.current_positions.values() if v == 0)
        cur_quantity = self.current_positions[ticker]
        quantity = 0
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            allocation = (self.current_holdings["cash"]/(no_position))
            mkt_quantity = int(allocation / self.bars.get_latest_bars(ticker)[0][5])  # Close price
            quantity = mkt_quantity
            order = OrderEvent(ticker, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            allocation = (self.current_holdings["cash"]/(no_position))
            mkt_quantity = int(allocation / self.bars.get_latest_bars(ticker)[0][5])  # Close price
            quantity = mkt_quantity
            order = OrderEvent(ticker, order_type, mkt_quantity, 'SELL')
    
        if direction == 'EXIT' and cur_quantity > 0:
            quantity = abs(cur_quantity)
            order = OrderEvent(ticker, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            quantity = abs(cur_quantity)
            order = OrderEvent(ticker, order_type, abs(cur_quantity), 'BUY')

        self.all_operations["quantity"].loc[self.all_operations["timeindex"] == signal.datetime] = quantity

        return order
    

    def update_operations_from_signal(self, signal):
        signal_dir = 0
        direction = signal.signal_type
        cur_quantity = self.current_positions[signal.ticker]

        if direction == 'LONG' and cur_quantity == 0:
            signal_dir = 1
        if direction == 'SHORT' and cur_quantity == 0:
            signal_dir = -1

        if direction == 'LONG' and cur_quantity < 0:
            signal_dir = 1
        if direction == 'SHORT' and cur_quantity > 0:
            signal_dir = -1

        if direction == 'EXIT' and cur_quantity > 0:
            signal_dir = -1
        if direction == 'EXIT' and cur_quantity < 0:
            signal_dir = 1

        new_operation = pd.DataFrame({"timeindex": [signal.datetime], #Timeindex
                                      "asset": [signal.ticker], #Ticker
                                      "direction": [signal_dir], #Direction
                                      "type": [signal.signal_type],
                                      "price": [self.bars.get_latest_bars(signal.ticker)[0][5]]}) #Close Price

        self.all_operations = self.all_operations.append(new_operation, ignore_index=True)

    def update_signal(self, event):
        if event.type == 'SIGNAL':
            self.update_operations_from_signal(event)
            order_event = self.generate_order(event)
            self.events.put(order_event)


    def create_equity_curve_dataframe(self):
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()

        self.equity_curve = curve
        
    def plot_equity_curve(self):
        # Generate the figure **without using pyplot**.
        fig = Figure(figsize=(9, 7))
        ax = fig.subplots()
        ax.plot(self.equity_curve.index, self.equity_curve['equity_curve'])
        ax.set_title('Equity Curve')
        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Equity')

        # Save it to a temporary buffer.
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        fig.savefig('equity_curve_' + self.ticker_list[0] + '.png')

        # Embed the result in the html output.
        img = base64.b64encode(buf.getbuffer()).decode("ascii")

        return img

    def create_trading_signals_chart(self, ticker, height, width):
        #Get Ticker Data
        data = self.bars.get_latest_all_bars_df(ticker)

        # Select buying and selling signals
        buys = self.all_operations.loc[(self.all_operations['direction'] == 1) & (self.all_operations['asset'] == ticker)]
        buys = buys.set_index('timeindex')

        sells = self.all_operations.loc[(self.all_operations['direction'] == -1) & (self.all_operations['asset'] == ticker)]
        sells = sells.set_index('timeindex')

        # Generate the figure **without using pyplot**.
        fig = Figure(figsize=(height, width))
        ax = fig.subplots()
        ax.plot(data.index, data['close'], label=ticker + 'Price')
        ax.plot(buys.index, data.loc[buys.index]['close'], '^', color='g')
        ax.plot(sells.index, data.loc[sells.index]['close'], 'v', color='r')

        return mpld3.fig_to_html(fig)


    def save_trading_signals_chart(self, ticker, height, width, start_date, last_date):
        from ta.trend import EMAIndicator

        #Get Ticker Data
        data = self.bars.get_latest_all_bars_df(ticker)
        data = data[(data.index >= start_date) & (data.index < last_date)]

        self.all_operations.to_excel("signals_" + self.ticker_list[0] + ".xlsx")

        # Select buying and selling signals
        buys = self.all_operations.loc[(self.all_operations['direction'] == 1) & (self.all_operations['asset'] == ticker)]
        buys = buys.set_index('timeindex')
        buys = buys[(buys.index >= start_date) & (buys.index < last_date)]

        sells = self.all_operations.loc[(self.all_operations['direction'] == -1) & (self.all_operations['asset'] == ticker)]
        sells = sells.set_index('timeindex')
        sells = sells[(sells.index >= start_date) & (sells.index < last_date)]

        # Generate the figure **without using pyplot**.
        fig = Figure(figsize=(height, width))
        ax = fig.subplots()
        ax.plot(data.index, data['close'], label=ticker + 'Price')
        ax.plot(buys.index, data.loc[buys.index]['close'], '^', color='g')
        ax.plot(sells.index, data.loc[sells.index]['close'], 'v', color='r')
        ax.set_title('Señales de Trading: ' + ticker)
        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Precio')

        fig.savefig(ticker + '.png')

        return mpld3.fig_to_html(fig)


    def list_trading_signals_chart(self, height, width):
        return {x: self.create_trading_signals_chart(x, height, width) for x in self.ticker_list}


    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio such
        as Sharpe Ratio and drawdown information.
        """
        total_return = self.equity_curve['equity_curve'][-1]

        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        max_dd, dd_duration = create_drawdowns(pnl)

        cagr = create_cagr(pnl)
        sortino_ratio = create_sortino_ratio(returns)

        stats = {"¿Es buena o no?": "Sí" if ((total_return - 1.0) * 100.0) > 10 else "No",
                 "Total Return": "%0.2f%%" % ((total_return - 1.0) * 100.0),
                 "Total Return Comp": total_return,
                 "PyG": "%0.2f" % (self.equity_curve['total'][-1] - self.starting_cash),
                 "Positive or Negative": True if ((total_return - 1.0) * 100.0) > 0 else False,
                 "Sharpe Ratio": "%0.2f" % sharpe_ratio,
                 "Max Drawdown": "%0.2f%%" % (max_dd * 100.0),
                 "Drawdown Duration": "%d" % dd_duration,
                 "Sortino Ratio": "%0.2f" % sortino_ratio,
                 "CAGR": "%0.4f%%" % cagr,
                 "Daily Return": "%0.4f%%" % returns.mean(),
                 "Daily Return Std": "%0.4f%%" % returns.std() }

        return stats