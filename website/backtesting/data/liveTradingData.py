from ...stock import Stock
from ...futures import Futures
from .dataHandler import DataHandler
from ..event.marketEvent import MarketEvent
import datetime
import pandas as pd

from datetime import date, datetime, timedelta
import pandas_datareader.data as web

class LiveTradingData(DataHandler):

    def __init__(self, events, ticker_list):
        self.events = events
        self.ticker_list = ticker_list

        self.ticker_data = {}
        self.latest_ticker_data = {}
        self.continue_backtest = True

        self._get_data_db()



    def _get_data_db(self):
        comb_index = None
        for t in self.ticker_list:
            todays_date = date.today()
            n = 30
            date_n_days_ago = date.today() - timedelta(days=n)
            yahoo_data = web.DataReader('ACC.NS', t, date_n_days_ago, todays_date)

            #add filter - get data, where column Volume is not 0
            yahoo_data = yahoo_data[yahoo_data.Volume != 0]

            self.ticker_data[t] = yahoo_data.tail(1)
                
            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.ticker_data[t].index
            else:
                comb_index.union(self.ticker_data[t].index)

            # Set the latest symbol_data to None
            self.latest_ticker_data[t] = []

        # Reindex the dataframes
        for t in self.ticker_list:
            self.ticker_data[t] = self.ticker_data[t].reindex(index=comb_index, method='pad').iterrows()

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