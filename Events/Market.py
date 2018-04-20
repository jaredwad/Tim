class Market:
    def __init__(self, direction, quantity, instrument='EUR_USD'):
        self.type = "MARKET"
        self.direction = direction
        self.quantity = quantity
        self.instrument = instrument
