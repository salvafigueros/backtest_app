import datetime
import numpy as np 
import pandas as pd 
import queue

from abc import ABCMeta, abstractmethod
from math import floor
from .event.fillEvent import FillEvent
from .event.orderEvent import OrderEvent


class PortfolioBacktesting(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_signal(self, event):
        raise NotImplementedError("Should implement update_signal()")

    
    @abstractmethod
    def update_fill(self, event):
        raise NotImplementedError("Should implement update_fill()")

