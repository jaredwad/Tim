class Tick:
    def __init__(self, candle, granularity):
        self.type = 'TICK'
        self.candle = candle
        self.granularity = granularity
