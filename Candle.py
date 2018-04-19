class Candle:
    def __init__(self, open, high, low, close):
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    @staticmethod
    def from_list(candles):
        open = candles[0].open
        close = candles[-1].close
        high = max([c.high for c in candles])
        low  = max([c.low  for c in candles])
        return Candle(open, high, low, close)
