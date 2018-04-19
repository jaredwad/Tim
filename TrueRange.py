from math import floor


class TrueRange:
    def __init__(self, length=20):
        self.length = length
        self.TR = []
        self.N = None

    def tick(self, candle):
        self.TR.append(max([candle.high - candle.low
                               , abs(candle.high - candle.close)
                               , abs(candle.low - candle.close)]))

        self.TR = self.TR[-self.length:]

    def ATR(self):
        if self.N:
            self.N = (self.N * (self.length - 1) + self.TR[-1]) / self.length
        else:
            self.N = self.SMA()

        return self.N

    def SMA(self):
        if len(self.TR) != self.length:
            return None

        return sum(self.TR) / self.length

    def unit(self, account_size, dollar_volitility):
        atr = self.ATR()
        if atr:
            return floor(.01 * float(account_size) / float(self.N * dollar_volitility))
        else:
            return 0
