from .event import Event


class FillEvent(Event):
    
    def __init__(self, timeindex, ticker, exchange, quantity, direction, fill_cost, commission=None):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.ticker = ticker
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        
        if commission is None:
            self.commission = 0
        else:
            self.commission = commission