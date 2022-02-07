import datetime
import queue

from abc import ABCMeta, abstractmethod
from .event.fillEvent import FillEvent
from .event.orderEvent import OrderEvent

class ExecutionHandler(object):

    __metaclass__ = ABCMeta


    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError("Should implement execute_order()")
