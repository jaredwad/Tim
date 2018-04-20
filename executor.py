class Executor:
    def __init__(self, initial_balance=100000):
        self.buy_queue = []
        self.trades_in_market = []
        self.account_balance = initial_balance

    def in_market(self):
        return len(self.trades_in_market) > 0

    def consume(self, event):
        if event.type == 'MARKET':
            self.buy_queue.append(event)

        if event.type == 'TICK':
            while len(self.buy_queue) > 0:
                self.execute_trade(self.buy_queue.pop(), event.candle.open)

    def execute_trade(self, market_order, price):
        if len(self.trades_in_market) == 0:
            self.trades_in_market.append(Order(market_order, price))

        else:
            for order in list(self.trades_in_market):
                if order.direction == market_order.direction:
                    order.quantity += market_order.quantity
                elif order.quantity > market_order.quantity:
                    order.quantity -= market_order.quantity
                else:
                    self.adjust_balance(order, price, -1)
                    market_order.quantity -= order.quantity
                    self.trades_in_market.remove(order)

                    if market_order.quantity > 0:
                        self.trades_in_market.append(market_order)

        self.adjust_balance(market_order, price)

    def adjust_balance(self, order, price, enter=1):
        self.account_balance -= order.quantity * price * enter * (1 if order.direction == 'BUY' else -1)


class Order:
    def __init__(self, market_event, price):
        self.direction = market_event.direction
        self.quantity = market_event.quantity
        self.instrument = market_event.instrument
        self.price = price
