from collections import deque
from functools import reduce

from rx.subjects import Subject

from Events.Close import Close
from Events.Fill import Fill
from Events.Indicator import Indicator
from Events.Market import Market
from Events.Tick import Tick


class Portfolio:
    def __init__(self, message_broker: Subject, initial_funds=100000):
        self.broker = message_broker
        self.account_funds = initial_funds
        self.order_queue = []
        self.active_orders = dict()
        self.PnL = []

        tick = self.broker.filter(lambda x: x.type == 'TICK')
        tick.filter(lambda x: x.granularity == 'H').subscribe(self.handle_tick)

        self.broker.filter(lambda x: x.type == 'MARKET').subscribe(self.handle_market)

        self.broker.filter(lambda x: x.type == 'INDICATOR').filter(lambda x: x.name == "Breakout") \
            .subscribe(self.handle_breakout)

    def handle_tick(self, tick: Tick):
        if len(self.order_queue) == 0:
            return

        orders = list(self.order_queue)
        self.order_queue = []

        price = tick.candle.close

        for order in orders:
            instrument = order.instrument

            fill_event = Fill(price, order.quantity, order.strategy_name, order.instrument)

            if instrument not in self.active_orders:
                self.active_orders[instrument] = []

            if len(self.active_orders[instrument]) > 0:
                self.cross_order(order, instrument, tick.candle.close)
            else:
                self.add_order(order, price, instrument)

            print("Filled {0} order - Total: {1}".format("BUY" if order.direction else "SELL", self.account_funds))
            self.broker.on_next(fill_event)

    def add_order(self, order, price, instrument):
        dir = 1 if order.direction else -1
        self.account_funds -= order.quantity * price * dir

        self.active_orders[instrument].append(Order(purchase_price=price, quantity=order.quantity, instrument=instrument
                                                    , strategy_name=order.strategy_name, direction=order.direction))

    def cross_order(self, order: Market, instrument: str, price: float):
        for active_order in self.active_orders[instrument]:
            if active_order.direction == order.direction:
                self.add_order(order, price, instrument)
                return

            order_quantity_abs = abs(order.quantity)
            active_quantity_abs = abs(active_order.quantity)

            dir = 1 if order.direction else -1

            if order_quantity_abs < active_quantity_abs:
                active_order.quantity += order.quantity
                self.account_funds -= order.quantity * price * dir

                dif = price - active_order.purchase_price
                dif = dif * dir

                self.PnL.append(dif * order.quantity)
                order.quantity = 0
                break
            elif order_quantity_abs > active_quantity_abs:
                close_event = Close(close_price=price, quantity=active_order.quantity, strategy_name=active_order.strategy_name, instrument=instrument)

                order.quantity += active_order.quantity
                self.account_funds -= active_order.quantity * price * dir

                dif = price - active_order.purchase_price
                dif = dif * dir

                self.active_orders[instrument].remove(active_order)

                self.PnL.append(dif * order.quantity)

                self.broker.on_next(close_event)

                continue
            else:
                close_event = Close(close_price=price, quantity=active_order.quantity, strategy_name=active_order.strategy_name, instrument=instrument)

                self.account_funds -= active_order.quantity * price * dir

                dif = price - active_order.purchase_price
                dif = dif * dir

                self.PnL.append(dif * order.quantity)

                self.active_orders[instrument].remove(active_order)
                order.quantity = 0

                self.broker.on_next(close_event)

                break
        if abs(order.quantity) > 0:
            self.active_orders[instrument].append(Order(purchase_price=price, quantity=order.quantity, instrument=order.instrument, strategy_name=order.strategy_name
                                                        , direction=order.direction))

    def handle_market(self, market_order: Market):
        print("Added Market order")
        self.order_queue.append(market_order)

    def handle_breakout(self, breakout: Indicator):
        is_up = breakout.payload
        instrument = breakout.instrument

        if instrument not in self.active_orders or len(self.active_orders[instrument]) == 0:
            return

        if is_up != self.active_orders[instrument][0].direction:
            self.order_queue.append(Market(is_up, -self.active_orders[instrument][0].quantity
                                           , self.active_orders[instrument][0].strategy_name, instrument))

    def print_pnl(self):
        s = reduce((lambda x, y: x + y), self.PnL)

        print("Total: {0}, Profit: {1}".format(self.account_funds, s))
        print(self.PnL)


class Order:
    def __init__(self, purchase_price: float, quantity: int, instrument: str, strategy_name: str, direction: bool):
        self.purchase_price = purchase_price
        self.quantity = quantity
        self.instrument = instrument
        self.strategy_name = strategy_name
        self.direction = direction
