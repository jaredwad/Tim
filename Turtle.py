from DataImporter import CSVDataImporter
from datetime import datetime

from Events.Tick import Tick
from ShortBreakout import ShortBreakout
from LongBreakout import LongBreakout
from TrueRange import TrueRange
from Indicator.Candle import Candle


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
        self.date = None

    def tick_day(self, event):
        if not (event.type == 'TICK' and event.granularity == 'D'):
            return
        candle = event.candle
        self.date = event.date

        self.short_breakout.tick_day(candle.close)
        self.long_breakout.tick_day(candle.close)
        self.true_range.tick(candle)

    def tick_hour(self, event):
        if not (event.type == 'TICK' and event.granularity == 'H'):
            return
        price = event.candle.close
        self.date = event.date

        self.short_breakout.tick_hour(price)
        self.long_breakout.tick_hour(price)

        if not self.in_market:
            enter = self.should_enter(price)
            if enter:
                self.enter(price, enter)
        else:
            if self.should_exit(price):
                self.exit_breakout.exited(price)
                self.exit(price)
            elif self.should_add(price):
                self.enter(price, "BUY" if self.enter_direction == 1 else "SELL")

    def should_enter(self, price):
        enter = self.short_breakout.should_enter(price)
        self.exit_breakout = self.short_breakout

        if enter is None:
            enter = self.long_breakout.should_enter(price)
            self.exit_breakout = self.long_breakout
            if enter is not None:
                print("Long said " + enter)
        else:
            print("Short said " + enter)

        return enter

    def enter(self, price, direction):
        self.in_market = True
        self.exit_breakout.entered(price)
        self.enter_direction = 1 if direction == 'BUY' else -1
        units = float(self.true_range.unit(self.account_size, self.dollar_volitility))
        self.open_trades.append((price, units))
        print("{0} {1} {2} at {3:.5f} {4}".format("Bought" if self.enter_direction == 1 else "Sold"
                                          , units * self.lot_size, "EUR_USD", price, self.date))

    def should_add(self, price):
        if len(self.open_trades) >= 4:
            return False

        last_price = self.open_trades[-1][0]

        if self.true_range.N is not None:
            dif = self.true_range.N * .5
        else:
            dif = dif = .002

        if self.enter_direction == 1:
            return price >= last_price + dif
        else:
            return price <= last_price - dif

    def should_exit(self, price):
        return self.exit_breakout.should_exit(price) or self.stop(price)

    def stop(self, price):
        last_price = self.open_trades[-1][0]

        if self.true_range.N is not None:
            dif = self.true_range.N * 2
        else:
            dif = dif = .002

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
        print("Closed Trade at {0:.5f} on {1} with a profit of {2}\n".format(price, self.date, total))

    def print_pnl(self):
        print("Ended with an account balance of {0}".format(self.account_size))
        print("profit was: {0}".format(sum(self.PnL)))


if __name__ == "__main__":
    importer = CSVDataImporter('/Users/jared/Dev/Tim/data/EUR_USD_very_long.csv')
    turtle = Turtle(ShortBreakout(length=20, exit_length=5), LongBreakout(length=30, exit_length=10))

    candles = []
    last_price = None
    last_day = None

    for index, row in importer.data.iterrows():
        date = datetime.strptime(index, "%Y-%m-%dT%H:%M:%S")

        if last_day is None:
            last_day = date.day

        if last_day != date.day:
            turtle.tick_day(Tick(Candle.from_list_of_candles(candles), 'D', date))
            candles = []
            last_day = date.day

        candles.append(Candle(row['open'], row['high'], row['low'], row['close']))

        turtle.tick_hour(Tick(candles[-1], 'H', date))

    #        print(date.day, row['close'])

    if turtle.in_market:
        turtle.exit(candles[-1].close)

    turtle.print_pnl()
