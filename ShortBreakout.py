import collections
from collections import deque


class ShortBreakout:
    def __init__(self, length=20, exit_length=10):
        self.length = length
        self.exit_length = exit_length
        self.data = []
        self.in_market = False
        self.current_direction = None
        self.enter_price = None
        self.won_last = False
        self.last_direction = None

    def tick_day(self, price):
        self.data.append(price)
        if len(self.data) > self.length:
            self.data[:1] = []
#        self.data = self.data[-self.length:]

    def tick_hour(self, price):
        # If we are testing a trend that we didn't officially enter
        if self.current_direction is not None and self.in_market is False:
            if self.should_exit(price):
                self.exited(price)

    def should_exit(self, price):
        if self.current_direction is None:
            raise ValueError('Not Currently in the market')

        self.last_direction = self.current_direction

        if self.current_direction == "BUY":
            if price < min(self.data[-self.exit_length:]):  # Exit on 10 day low
                return True
            return False

        if self.current_direction == "SELL":
            if price > max(self.data[-self.exit_length:]):  # Exit on 10 day high
                return True
            return False

        raise ValueError("current_direction set to invalid value. Expected"
                         + " \'BUY\' or \'SELL\' but recieved "
                         + self.current_direction)

    def should_enter(self, price):
        # Dont enter if there's insufficient data or we are still checking the last trend
        if len(self.data) < self.length or self.current_direction is not None:
            return None

        if price > max(self.data):
            print("Short breakout buy")
            return self.check_last("BUY")

        elif price < min(self.data):
            print("Short breakout sell")
            return self.check_last("SELL")

    def check_last(self, direction="BUY"):
        self.current_direction = direction
        if self.won_last and self.last_direction == direction:
            self.won_last = False
            print("won last, so not entering")
            return None

        return direction

    def entered(self, price):
        self.enter_price = price
        self.in_market = True

    def exited(self, price):
        self.won_last = self.was_profitable(price)

        self.in_market = False
        self.current_direction = None

    def was_profitable(self, price):
        profit = price - self.enter_price

        if self.current_direction == 'SELL':
            profit = -profit

        return profit > 0
