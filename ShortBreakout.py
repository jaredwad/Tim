class ShortBreakout:
    def __init__(self, length=20, exit_length=10):
        self.length = length
        self.exit_length = exit_length
        self.data = []
        self.in_market = False
        self.current_direction = None
        self.enter_price = None
        self.won_last = False
        self.last_price = None
        self.last_direction = None

    def tick_day(self, price):
        self.data.append(price)
        self.data = self.data[-self.length:]

    def tick_hour(self, price):
        self.last_price = price

        # If we are testing a trend that we didn't officially enter
        if self.current_direction is not None and self.in_market is False:
            if self.should_exit():
                self.won_last = self.was_profitable()
                self.current_direction = None
                self.enter_price = None

    def should_exit(self):
        if self.current_direction is None:
            raise ValueError('Not Currently in the market')

        self.last_direction = self.current_direction

        if self.current_direction == "BUY":
            if self.last_price < min(self.data[-self.exit_length:]):  # Exit on 10 day low
                self.in_market = False
                return True
            return False

        if self.current_direction == "SELL":
            if self.last_price > max(self.data[-self.exit_length:]):  # Exit on 10 day high
                self.in_market = False
                return True
            return False

        raise ValueError("current_direction set to invalid value. Expected"
                         + " \'BUY\' or \'SELL\' but recieved "
                         + self.current_direction)

    def was_profitable(self):
        profit = self.last_price - self.enter_price

        if self.current_direction == 'SELL':
            profit = -profit

        return profit > 0

    def should_enter(self):
        # Dont enter if there's insufficient data or we are still checking the last trend
        if len(self.data) < self.length or self.current_direction is not None:
            return None

        self.enter_price = self.last_price

        if self.last_price > max(self.data):
            print("Short breakout buy")
            return self.check_last("BUY")

        elif self.last_price < min(self.data):
            print("Short breakout sell")
            return self.check_last("SELL")

    def check_last(self, direction="BUY"):
        self.current_direction = direction

        if self.won_last and self.last_direction == direction:
            return None

        self.in_market = True
        return direction
