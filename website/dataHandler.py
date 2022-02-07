from abc import ABCMeta, abstractmethod

from .event.marketEvent import MarketEvent

class DataHandler(object):


    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, ticker, N=1):
        raise NotImplementedError("Should implement get_latest_bars()")


    @abstractmethod
    def update_bars(self):
        raise NotImplementedError("Should implement update_bars()")

    