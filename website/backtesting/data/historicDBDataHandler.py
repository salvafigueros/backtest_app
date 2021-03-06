from ...stock import Stock
from ...futures import Futures
from .dataHandler import DataHandler
from ..event.marketEvent import MarketEvent
import datetime
import pandas as pd

class HistoricDBDataHandler(DataHandler):

    def __init__(self, events, ticker_list, start_dt, end_dt):
        self.events = events
        self.ticker_list = ticker_list
        self.start_dt = start_dt
        self.end_dt = end_dt

        self.ticker_data = {}
        self.latest_ticker_data = {}
        self.continue_backtest = True

        self._get_data_db()



    def _get_data_db(self):
        comb_index = None
        for t in self.ticker_list:
            stock = Stock.get_stock_by_ticker(t)
            future = Futures.get_futures_by_ticker(t)

            if stock:
                self.ticker_data[t] = stock.get_stock_prices_dates(self.start_dt, self.end_dt)
            elif future:
                self.ticker_data[t] = future.get_futures_prices_dates(self.start_dt, self.end_dt)

            if stock or future:
                
                if comb_index is None:
                    comb_index = self.ticker_data[t].index
                else:
                    comb_index.union(self.ticker_data[t].index)

                self.latest_ticker_data[t] = []

        for t in self.ticker_list:
            self.ticker_data[t] = self.ticker_data[t].reindex(index=comb_index, method='pad').iterrows()
            print(self.ticker_data[t])

    
        self.start_date = comb_index[0]

    
    
    def _get_new_bar(self, ticker):
        """
        Returns the latest bar from the data feed as a tuple of 
        (ticker, datetime, open, high, low, close, adjusted_close, volume).
        """
        for b in self.ticker_data[ticker]:
            yield tuple([ticker, datetime.datetime.strptime(b[0].strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'), 
                        b[1][0], b[1][1], b[1][2], b[1][3], b[1][4], b[1][5]])

    def get_latest_bars(self, ticker, N=1):
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print("That ticker is not available in the historical data set.")
        else:
            return bars_list[-N:]

    
    def get_latest_bars_df(self, ticker, N=1):
        list_tuples = self.get_latest_bars(ticker, N)
        df = pd.DataFrame(list_tuples, columns=["ticker", "datetime", "open", "high", "low", "close", "adjusted_close", "volume"])
        df = df.set_index('datetime')
        return df


    def get_latest_all_bars(self, ticker):
        try:
            bars_list = self.latest_ticker_data[ticker]
        except KeyError:
            print("That ticker is not available in the historical data set.")
        else:
            return bars_list

    
    def get_latest_all_bars_df(self, ticker):
        list_tuples = self.get_latest_all_bars(ticker)
        df = pd.DataFrame(list_tuples, columns=["ticker", "datetime", "open", "high", "low", "close", "adjusted_close", "volume"])
        df = df.set_index('datetime')
        return df


    def update_bars(self):
        for t in self.ticker_list:
            try:
                bar = self._get_new_bar(t).__next__()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_ticker_data[t].append(bar)
        self.events.put(MarketEvent())

    def get_start_date(self):
        if self.start_date:
            return self.start_date
    
        return None
