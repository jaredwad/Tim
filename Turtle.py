import numpy as np
from DataImporter import CSVDataImporter
from datetime import datetime
from ShortBreakout import ShortBreakout
from LongBreakout import LongBreakout
from TrueRange import TrueRange
from Candle import Candle


class Turtle:
    def __init__(self, short_breakout, long_breakout, true_range=TrueRange()):
        self.short_breakout = short_breakout
        self.long_breakout = long_breakout
        self.in_market = False
        self.enter_direction = None
        self.PnL = []
        self.exit_breakout = None
        self.true_range = true_range
        self.open_trades = []
        self.account_size = float(100000)
        self.dollar_volitility = float(1000)
        self.lot_size = float(10)

    def tick_day(self, candle):
        self.short_breakout.tick_day(candle.close)
        self.long_breakout.tick_day(candle.close)
        self.true_range.tick(candle)

    def tick_hour(self, price):
        self.short_breakout.tick_hour(price)
        self.long_breakout.tick_hour(price)

        if not self.in_market:
            enter = self.should_enter(price)
            if enter:
                self.enter(price, enter)
        else:
            if self.should_exit(price):
                self.exit(price)
            elif self.should_add(price):
                self.enter(price, "BUY" if self.enter_direction == 1 else "SELL")

    def should_enter(self, price):
        enter = self.short_breakout.should_enter()
        self.exit_breakout = self.short_breakout

        if enter is None:
            enter = self.long_breakout.should_enter()
            self.exit_breakout = self.long_breakout

        return enter

    def enter(self, price, direction):
        self.in_market = True
        self.enter_direction = 1 if direction == 'BUY' else -1
        units = float(self.true_range.unit(self.account_size, self.dollar_volitility))
        self.open_trades.append((price, units))
        print("{0} {1} {2} at {3}".format("Bought" if self.enter_direction == 1 else "Sold"
                                          , units * self.lot_size, "EUR_USD", price))

    def should_add(self, price):
        if len(self.open_trades) >= 4:
            return False

        last_price = self.open_trades[-1][0]

        dif = self.true_range.N * .5

        if self.enter_direction == 1:
            return price >= last_price + dif
        else:
            return price <= last_price - dif

    def should_exit(self, price):
        return self.exit_breakout.should_exit() or self.stop(price)

    def stop(self, price):
        last_price = self.open_trades[-1][0]

        dif = self.true_range.N * 2

        if self.enter_direction == 1:
            return price <= last_price - dif
        else:
            return price >= last_price + dif

    def exit(self, price):
        self.in_market = False

        total = sum([(price - enter_price) * self.enter_direction * units * self.lot_size for enter_price, units in
                     self.open_trades])

        self.account_size += total

        self.PnL.append(total)

        self.open_trades = []
        self.enter_direction = None
        print("Closed Trade at {0}\n".format(price))

    def print_pnl(self):
        print("Ended with an account balance of {0}".format(self.account_size))
        print("profit was: {0}".format(sum(self.PnL)))


if __name__ == "__main__":
    importer = CSVDataImporter('/Users/jared/Dev/Tim/data/EUR_USD.csv')
    turtle = Turtle(ShortBreakout(length=20, exit_length=6), LongBreakout(length=30, exit_length=10))

    candles = []
    last_price = None
    last_day = None

    for index, row in importer.data.iterrows():
        date = datetime.strptime(index, "%Y-%m-%dT%H:%M:%S")

        if last_day is None:
            last_day = date.day

        if last_day != date.day:
            turtle.tick_day(Candle.from_list(candles))
            candles = []
            last_day = date.day

        candles.append(Candle(row['open'], row['high'], row['low'], row['close']))

        turtle.tick_hour(row['close'])

    #        print(date.day, row['close'])

    turtle.print_pnl()
