class Market:
    def __init__(self, direction: bool, quantity: int, strategy_name: str, instrument: str = 'EUR_USD'):
        self.type = "MARKET"
        self.direction = direction
        self.quantity = quantity
        self.strategy_name = strategy_name
        self.instrument = instrument
