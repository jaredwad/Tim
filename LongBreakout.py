class LongBreakout:
    def __init__(self, length=55, exit_length=20):
        self.length = length
        self.exit_length = exit_length
        self.data = []
        self.last_price = None
        self.current_direction = None

    def tick_day(self, price):
        self.data.append(price)
        self.data = self.data[-self.length:]

    def tick_hour(self, price):
        self.last_price = price

    def should_enter(self):
        if self.current_direction is not None or len(self.data) < self.length:
            return None

        if self.last_price > max(self.data):
            self.current_direction = "BUY"
            return "BUY"

        elif self.last_price < min(self.data):
            self.current_direction = "SELL"
            return "SELL"

    def should_exit(self):
        if self.current_direction is None:
            raise ValueError('Not Currently in the market')

        if self.current_direction == "BUY":
            if self.last_price < min(self.data[-self.exit_length:]): # Exit on 10 day low
                return True
            return False

        if self.current_direction == "SELL":
            if self.last_price > max(self.data[-self.exit_length:]): # Exit on 10 day high
                return True
            return False

        raise ValueError("current_direction set to invalid value. Expected"
                         + " \'BUY\' or \'SELL\' but recieved "
                         + self.current_direction)
