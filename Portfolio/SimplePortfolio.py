from collections import defaultdict
from functools import reduce

from Events.Cancel import Cancel
from Events.Candle import Candle
from Events.Close import Close
from Events.Fill import Fill
from Events.Market import Market
from MessageBroker.MessageBroker import MessageBroker


class SimplePortfolio:
    def __init__(self, message_broker: MessageBroker, initial_funds: float):
        self.PnL = []
        self.account_funds = initial_funds
        self.open_queue = []
        self.close_queue = []
        self.current_holdings = defaultdict(lambda: None)

        self.message_broker = message_broker

        self.message_broker.get_candles().subscribe(self.handle_candle)

        self.message_broker.get_market().subscribe(self.handle_market)

    def handle_candle(self, candle: Candle):
        self.close_valid_positions(candle.open)
        self.open_new_positions(candle.open)
        self.mark_positions_for_close(candle.close)

    def handle_market(self, order: Market):
        self.open_queue.append(order)

    def close_valid_positions(self, current_price: float):
        while len(self.close_queue) > 0:
            order = self.close_queue.pop(0)
            profit = order.calculate_profit(current_price)

            self.account_funds += profit
            self.PnL.append(profit)

            self.message_broker.submit_event(Close(current_price, order.quantity, order.strategy_name
                                                   , order.instrument))

    def mark_positions_for_close(self, closing_price):
        closing_positions = self.get_closing_positions(closing_price)
        self.close_queue.extend(closing_positions)

    def get_closing_positions(self, closing_price: float):
        orders_to_close = []
        for k in list(self.current_holdings.keys()):
            if self.current_holdings[k] is None:
                continue

            if self.current_holdings[k].should_exit(closing_price):
                orders_to_close.append(self.current_holdings.pop(k))

        return orders_to_close

    def open_new_positions(self, current_price: float):
        while len(self.open_queue) > 0:
            order = self.open_queue.pop(0)
            self.open_position(order, current_price)

    def open_position(self, order: Market, current_price: float):
        if self.current_holdings[order.instrument] is not None:
            self.cancel_order(order)
            return

        new_order = Order(order.instrument, order.strategy_name, order.direction, order.quantity, current_price
                          , order.take_profit, order.stop_loss, order.is_trailing_stop)

        self.current_holdings[order.instrument] = new_order

        self.message_broker.submit_event(Fill(current_price, order.quantity, order.strategy_name
                                              , order.instrument))

    def cancel_order(self, order: Market):
        self.message_broker.submit_event(Cancel(order.quantity, order.strategy_name, order.instrument))

    def print_pnl(self):
        s = reduce((lambda x, y: x + y), self.PnL)

        print("Total: {0}, Profit: {1}".format(self.account_funds, s))
        print(self.PnL)


class Order:
    def __init__(self, instrument: str, strategy_name: str, direction: bool, quantity: int, purchase_price: float
                 , take_profit: float=None, stop_loss: float=None, trailing_stop=False):
        self.instrument = instrument
        self.strategy_name = strategy_name
        self.direction = direction
        self.quantity = quantity

        self.initial_value = quantity * purchase_price

        if stop_loss is not None:
            if not trailing_stop:
                self.stop_loss = create_stop_loss(purchase_price, stop_loss, direction)
            else:
                self.stop_loss = create_trailing_stop_loss(purchase_price, stop_loss, direction)
        else:
            self.stop_loss = lambda x: False

        if take_profit is not None:
            self.take_profit = create_take_profit(purchase_price, take_profit, direction)
        else:
            self.take_profit = lambda x: False

    def should_exit(self, current_price: float):
        return self.stop_loss(current_price) or self.take_profit(current_price)

    def get_current_value(self, current_price: float):
        return self.quantity * current_price

    def get_initial_value(self):
        return self.initial_value

    def calculate_profit(self, closing_price):
        closing_value = self.get_current_value(closing_price)
        initial_value = self.get_initial_value()

        if self.direction:
            profit = closing_value - initial_value
        else:
            profit = initial_value - closing_value

        return profit


def create_stop_loss(purchace_price: float, stop_loss: float, direction_is_up: bool):
    exit_price = purchace_price - (stop_loss if direction_is_up else -stop_loss)

    def should_exit(current_price: float):
        return (current_price <= exit_price) if direction_is_up else (current_price >= exit_price)

    return should_exit


# Create a new stop loss every time a better price comes along
def create_trailing_stop_loss(purchace_price: float, stop_loss: float, direction_is_up: bool):
    sl = create_stop_loss(purchace_price, stop_loss, direction_is_up)
    best_price = purchace_price

    def should_exit(current_price: float, ):
        nonlocal sl, best_price

        if current_price > best_price and direction_is_up:
            best_price = current_price
            sl = create_stop_loss(best_price, stop_loss, direction_is_up)
        elif current_price < best_price and not direction_is_up:
            best_price = current_price
            sl = create_stop_loss(best_price, stop_loss, direction_is_up)

        return sl(current_price)

    return should_exit


# Take profits are really just reverse stop losses
def create_take_profit(purchase_price: float, take_profit: float, direction_is_up: bool):
    return create_stop_loss(purchase_price, take_profit, not direction_is_up)
