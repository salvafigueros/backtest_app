from .strategy import Strategy
from ..event.signalEvent import SignalEvent
import numpy as np 
import pandas as pd 

class ShortMinStrategy(Strategy):
   
    def __init__(self, bars, events, time_frame, exit_trade, exit_configuration):
        self.bars = bars
        self.ticker_list = self.bars.ticker_list 
        self.events = events
        self.time_frame = time_frame
        self.exit_trade = exit_trade
        self.exit_configuration = exit_configuration

        self.bought = self._calculate_initial_bought()
        self.num_bars = self._calculate_initial_num_bars()
        self.minimum = self._calculate_initial_minimum()
        self.days_strategy = self._calculate_initial_days_strategy()
        self.trailing_stop = self._calculate_initial_trailing_stop()

    def get_name(self):
        return "shortmin"

    def _calculate_initial_bought(self):
        bought = {}
        for t in self.ticker_list:
            bought[t] = False

        return bought

    def _calculate_initial_num_bars(self):
        num_bars = {}
        for t in self.ticker_list:
            num_bars[t] = 0

        return num_bars

    def _calculate_initial_minimum(self):
        minimum = {}
        for t in self.ticker_list:
            minimum[t] = None

        return minimum

    def _update_minimum(self, ticker, bars):
        if self.minimum[ticker] is None:
            self.minimum[ticker] = bars[0][4] #Low
        else:
            self.minimum[ticker] = min(self.bars.get_latest_bars(ticker, N=self.time_frame), key=lambda item:item[4])[4]

    def _calculate_initial_days_strategy(self):
        days_strategy = {}
        for t in self.ticker_list:
            days_strategy[t] = 0

        return days_strategy

    def _calculate_initial_trailing_stop(self):
        trailing_stop = {}
        for t in self.ticker_list:
            trailing_stop[t] = None

        return trailing_stop


    def _calculate_atr_latest_bar(self, ticker):
        data = self.bars.get_latest_bars_df(ticker, N=self.time_frame*self.exit_configuration+1)

        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        true_range.drop(index=true_range.index[0],
                        axis=0,
                        inplace=True)

        atr = true_range.sum()/(self.time_frame*self.exit_configuration)
        #atr = true_range.rolling(self.time_frame).sum()/self.time_frame

        return atr

    def _update_trailing_stop(self, ticker, bars):
        if not self.bought[ticker]:
            self.trailing_stop[ticker] = None
        else:
            if self.trailing_stop[ticker] is None:
                #Calculate trailing_stop for the first day of a position
                self.trailing_stop[ticker] = bars[1][5] + (self._calculate_atr_latest_bar(ticker)*self.exit_configuration)
            else:
                #Calculate trailing_stop for the rest of the days of a position
                if bars[0][5] < bars[1][5]:
                    #Adjust the price of the trailing_stop as the position goes with you
                    self.trailing_stop[ticker] = bars[1][5] + (self._calculate_atr_latest_bar(ticker)*self.exit_configuration)

        

    def calculate_signals(self, event):

        if event.type == "MARKET":
            for t in self.ticker_list:
                bars = self.bars.get_latest_bars(t, N=1)
                if bars is not None and bars != []:
                    self.num_bars[t] += 1

                    if(self.num_bars[t] > self.time_frame):
                        if self.bought[t] == False:
                            if bars[0][4] <= self.minimum[t]:
                                signal = SignalEvent(bars[0][0], bars[0][1], 'SHORT')
                                self.events.put(signal)
                                self.bought[t] = True 
                                self._update_trailing_stop(t, self.bars.get_latest_bars(t, N=2))
                        else:
                            self.days_strategy[t] += 1
                            if self.exit_trade == "exit_time":
                                if self.days_strategy[t] == int(self.exit_configuration * 0.5 * self.time_frame):
                                    signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT')
                                    self.events.put(signal)
                                    self.bought[t] = False 
                                    self.days_strategy[t] = 0
                            else:
                                if bars[0][3] >= self.trailing_stop[t]:
                                    signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT')
                                    self.events.put(signal)
                                    self.bought[t] = False

                                self._update_trailing_stop(t, self.bars.get_latest_bars(t, N=2))
                                

                    self._update_minimum(t, bars)