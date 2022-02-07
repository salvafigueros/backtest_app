from .event import Event


class MarketEvent(Event):

    def __init__(self):
        self.type = 'MARKET'

    