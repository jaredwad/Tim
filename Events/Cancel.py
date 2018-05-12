class Cancel:
    def __init__(self, quantity: int, strategy_name: str, instrument: str):
        self.type = Cancel.get_type()
        self.quantity = quantity
        self.strategy_name = strategy_name
        self.instrument = instrument

    @staticmethod
    def get_type():
        return 'CANCEL'
