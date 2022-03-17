from.event import Event

class OrderEvent(Event):

    def __init__(self, ticker, order_type, quantity, direction):
        self.type = 'ORDER'
        self.ticker = ticker
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        print ("Order: Ticker=%s, Type=%s, Quantity=%s, Direction=%s" % \
            (self.ticker, self.order_type, self.quantity, self.direction))