class Market:
    def __init__(self, direction: bool, quantity: int, strategy_name: str, instrument: str = 'EUR_USD'
                 , take_profit: float=None, stop_loss: float=None, is_trailing_stop: bool=False):
        self.type = Market.get_name()
        self.direction = direction
        self.quantity = quantity
        self.strategy_name = strategy_name
        self.instrument = instrument
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.is_trailing_stop = is_trailing_stop

    @staticmethod
    def get_name():
        return 'MARKET'
