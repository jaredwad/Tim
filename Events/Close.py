class Close:
    def __init__(self, close_price: float, quantity: int, strategy_name: str, instrument: str):
        self.type = 'CLOSE'
        self.close_price = close_price
        self.quantity = quantity
        self.strategy_name = strategy_name
        self.instrument = instrument
