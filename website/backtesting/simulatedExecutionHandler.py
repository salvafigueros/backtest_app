from .executionHandler import ExecutionHandler
from .event.fillEvent import FillEvent
import datetime

class SimulatedExecutionHandler(ExecutionHandler):
    
    def __init__(self, events):
        self.events = events

    def execute_order(self, event):

        if event.type == 'ORDER':
            fill_event = FillEvent(datetime.datetime.utcnow(), event.ticker,
                                   '', event.quantity, event.direction, None)
            self.events.put(fill_event)



            