from .strategy import Strategy
from ..event.signalEvent import SignalEvent
import numpy as np
import pandas as pd

class BuyAndHoldStrategy(Strategy):
    """
    This is an extremely simple strategy that goes LONG all of the 
    symbols as soon as a bar is received. It will never exit a position.

    It is primarily used as a testing mechanism for the Strategy class
    as well as a benchmark upon which to compare other strategies.
    """

    def __init__(self, bars=None, events=None):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        """
        self.bars = bars
        self.events = events

        if self.bars is not None:
            self.set_bars(self.bars, self.bars.ticker_list)


    def set_bars(self, bars, ticker_list):
        self.bars = bars

        if self.bars:
            self.ticker_list = self.bars.ticker_list 
            self.bought = self._calculate_initial_bought()

        return 


    def get_name(self):
        return "buyandhold"


    def to_html(self):
        html = """ 
                <ul class="list-group-item widget-49-meeting-points" style="list-style-type:none;">
                    <li class="widget-49-meeting-item"><span> Estrategia: """ + self.get_name() + """</span></li>
                </ul>
               """
     
        return html


    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to False.
        """
        bought = {}
        for s in self.ticker_list:
            bought[s] = False
        return bought

    def calculate_signals(self, event):
        """
        For "Buy and Hold" we generate a single signal per symbol
        and then no additional signals. This means we are 
        constantly long the market from the date of strategy
        initialisation.

        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for s in self.ticker_list:
                bars = self.bars.get_latest_bars(s, N=1)
                if bars is not None and bars != []:
                    if self.bought[s] == False:
                        # (Symbol, Datetime, Type = LONG, SHORT or EXIT)
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG')
                        self.events.put(signal)
                        self.bought[s] = True