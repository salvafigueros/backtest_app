import datetime
import numpy as np
import pandas as pd
import queue

from abc import ABCMeta, abstractmethod

class Strategy(object):
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("Should implement calculate_signals()")