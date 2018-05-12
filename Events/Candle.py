from functools import reduce


class Candle:
    def __init__(self, open, high, low, close, volume, time):
        self.type = Candle.get_name()
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.time = time

    def to_list(self):
        return [self.open, self.high, self.low, self.close, self.volume]

    @staticmethod
    def from_list_of_candles(candles):
        open = candles[0].open
        close = candles[-1].close
        high = max([c.high for c in candles])
        low  = max([c.low  for c in candles])
        volume = reduce((lambda x, y: x + y.volume), candles)
        return Candle(open, high, low, close, volume)

    @staticmethod
    def get_name():
        return 'CANDLE'
