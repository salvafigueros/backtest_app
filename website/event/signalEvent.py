from .event import Event

class SignalEvent(Event):

    def __init__(self, ticker, datetime, signal_type):
        self.type = 'SIGNAL'
        self.ticker = ticker
        self.datetime = datetime
        self.signal_type = signal_type

        