from .performance import create_sharpe_ratio, create_drawdowns, create_cagr, create_sortino_ratio
from .portfolioBacktesting import PortfolioBacktesting
from math import floor
from .event.orderEvent import OrderEvent
import pandas as pd 
import plotly.graph_objects as go
import matplotlib.pyplot as plt


class ConservativePortfolio(PortfolioBacktesting):


    def __init__(self, bars, events, start_date, starting_cash=100000.0):
        self.bars = bars
        self.events = events
        self.ticker_list = self.bars.ticker_list
        self.start_date = start_date
        self.starting_cash = starting_cash

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict( (k,v) for k, v in [(t, 0) for t in self.ticker_list] )

        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

        self.all_returns = self.construct_all_returns()
        self.latest_positions = dict( (k,v) for k, v in [(t, 0) for t in self.ticker_list] )

        #self.kelly_criterion = self.calculate_all_kelly_criterions()


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

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current 
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OLHCVI).

        Makes use of a MarketEvent from the events queue.
        """
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
            market_value = self.current_positions[t] * bars[t][0][5]
            dh[t] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)


    def update_positions_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the position matrix
        to reflect the new position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        self.current_positions[fill.ticker] += fill_dir*fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """
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
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_returns_from_fill(self, fill):
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Without commissions
        if fill_dir != 0 and self.latest_positions[fill.ticker] != 0:
            fill_cost = self.bars.get_latest_bars(fill.ticker)[0][5]  # Close price
            cost = fill_dir * fill_cost * fill.quantity
            return_position = 0
            if fill_dir == 1:
                return_position = self.latest_positions[fill.ticker] + (cost)
            else:
                return_position = self.latest_positions[fill.ticker] + (cost)

            self.all_returns[fill.ticker] += return_position
            self.latest_positions[fill.ticker] = 0
        elif fill_dir != 0 and self.latest_positions[fill.ticker] == 0:
            fill_cost = self.bars.get_latest_bars(fill.ticker)[0][5]  # Close price
            self.latest_positions[fill.ticker] = fill_dir * fill_cost * fill.quantity

        #self.current_holdings[fill.ticker] += cost


    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
            self.update_returns_from_fill(event)


    def calculate_position_sizing():
        """
        Calculates the number of stocks/futures based on 
         the rule of 2%
        """
        pass


    def generate_naive_order(self, signal):
        """
        Simply transacts an OrderEvent object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The SignalEvent signal information.
        """
        order = None

        ticker = signal.ticker
        direction = signal.signal_type
        #strength = signal.strength

        #mkt_quantity = floor(100 * strength)
        mkt_quantity = floor(50)
        cur_quantity = self.current_positions[ticker]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(ticker, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(ticker, order_type, mkt_quantity, 'SELL')   
    
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(ticker, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(ticker, order_type, abs(cur_quantity), 'BUY')
        return order
    

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)


    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve
 

    def plot_equity_curve(self):
        plt.plot(self.equity_curve.index, self.equity_curve['equity_curve'])
        plt.title('Equity Curve Vs Year')
        plt.xlabel('Year')
        plt.ylabel('Equity Curve')
        plt.savefig('/static/equity_curve.png')

        return '/static/equity_curve.png'

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

        stats = [("¿Es buena o no?", "Sí" if ((total_return - 1.0) * 100.0) > 10 else "No"),
                 ("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration),
                 ("Sortino Ratio", "%0.2f" % sortino_ratio),
                 ("CAGR", "%0.4f%%" % cagr)]
        return stats