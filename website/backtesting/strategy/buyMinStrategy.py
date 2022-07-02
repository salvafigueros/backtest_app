from .strategy import Strategy
from ..event.signalEvent import SignalEvent
import numpy as np 
import pandas as pd
from .strategyBuyShortMaxMin import StrategyBuyShortMaxMin


class BuyMinStrategy(Strategy):
    
    def __init__(self, time_frame, exit_trade, exit_configuration, strategy_id=None, bars=None, events=None):
        self.id = strategy_id
        self.bars = bars
        self.events = events
        self.time_frame = time_frame
        self.exit_trade = exit_trade
        self.exit_configuration = exit_configuration

        self.started = False

        if self.bars:
            self.ticker_list = self.bars.ticker_list 
            self.bought = self._calculate_initial_bought()
            self.num_bars = self._calculate_initial_num_bars()
            self.minimum = self._calculate_initial_minimum()
            self.days_strategy = self._calculate_initial_days_strategy()
            self.trailing_stop = self._calculate_initial_trailing_stop()


    def set_bars(self, bars, ticker_list):
        self.bars = bars

        if self.bars:
            self.ticker_list = self.bars.ticker_list 
            self.bought = self._calculate_initial_bought()
            self.num_bars = self._calculate_initial_num_bars()
            self.minimum = self._calculate_initial_minimum()
            self.days_strategy = self._calculate_initial_days_strategy()
            self.trailing_stop = self._calculate_initial_trailing_stop()

        return 


    def get_name(self):
        return "buymin"


    def get_name_to_html(self):
        return "Comprar Mínimos"


    def exit_trade_to_html(self):
        if self.exit_trade == "exit_time":
            return "Salida por Tiempo"
        elif self.exit_trade == "trailing_stop":
            return "Salida por Trailing Stop"

        return ""

    def exit_configuration_to_html(self):
        if self.exit_trade == "exit_time":
            if self.exit_configuration == 1:
                return "Nº de Días de cada Operación: 50'%' de los días del Marco Temporal"
            elif self.exit_configuration == 2:
                return " Nº de Días de cada Operación: 100'%' de los días del Marco Temporal"
            elif self.exit_configuration == 3:
                return "Nº de Días de cada Operación: 150'%' de los días del Marco Temporal"

        elif self.exit_trade == "trailing_stop":
            if self.exit_configuration in (1, 2, 3):
                return "Multiplicador ATR: " + str(self.exit_configuration)
            
        return ""


    def to_html(self):
        html = """ 
                <ul class="list-group-item widget-49-meeting-points" style="list-style-type:none;">
                    <li class="widget-49-meeting-item"><span> Estrategia: """ + self.get_name_to_html() + """</span></li>
                    <li class="widget-49-meeting-item"><span> Marco Temporal: """ + str(self.time_frame) + """ días </span></li>
                    <li class="widget-49-meeting-item"><span> Tipo de Salida: """ + self.exit_trade_to_html() + """ </span></li>
                    <li class="widget-49-meeting-item"><span>""" + self.exit_configuration_to_html() + """ </span></li>
                </ul>
               """
     
        return html

    def save_strategy(self, strategy_id):
        return StrategyBuyShortMaxMin.create_strategy(strategy_id, self.get_name(), self.time_frame, self.exit_trade, self.exit_configuration)

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
                self.trailing_stop[ticker] = bars[1][5] - (self._calculate_atr_latest_bar(ticker)*self.exit_configuration)
            else:
                #Calculate trailing_stop for the rest of the days of a position
                if bars[0][5] < bars[1][5]:
                    #Adjust the price of the trailing_stop as the position goes with you
                    self.trailing_stop[ticker] = bars[1][5] - (self._calculate_atr_latest_bar(ticker)*self.exit_configuration)

        

    def calculate_signals(self, event):

        if event.type == "MARKET":
            for t in self.ticker_list:
                bars = self.bars.get_latest_bars(t, N=1)
                if bars is not None and bars != []:
                    self.num_bars[t] += 1

                    if(self.num_bars[t] > self.time_frame):
                        self.started = True
                        if self.bought[t] == False:
                            if bars[0][4] <= self.minimum[t]:
                                signal = SignalEvent(bars[0][0], bars[0][1], 'LONG')
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
                                if bars[0][4] <= self.trailing_stop[t]:
                                    signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT')
                                    self.events.put(signal)
                                    self.bought[t] = False

                                self._update_trailing_stop(t, self.bars.get_latest_bars(t, N=2))
                                

                    self._update_minimum(t, bars)





                    
                