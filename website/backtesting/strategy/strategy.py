import datetime
import numpy as np
import pandas as pd
import queue
import mysql.connector

from abc import ABCMeta, abstractmethod

class Strategy(object):
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("Should implement calculate_signals()")