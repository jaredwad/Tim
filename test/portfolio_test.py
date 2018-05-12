import unittest
from datetime import datetime

from rx.subjects import Subject

from Events.Candle import Candle
from Events.Market import Market
from Events.Tick import Tick
from Portfolio.Portfolio import Portfolio


class PortfoilioTest(unittest.TestCase):
    def setUp(self):
        self.message_broker = Subject()
        self.portfolio = Portfolio(self.message_broker, initial_funds=100000)

    def test_tick(self):
        self.portfolio.order_queue.append(Market(True, 1000, "", "EUR_USD"))
        self.message_broker.on_next(Tick(Candle(1,1,1,1,1), 'H', datetime.now(), 'EUR_USD'))
        self.assertEqual(len(self.portfolio.order_queue), 0)
        self.assertEqual(len(self.portfolio.active_orders), 1)

    def test_cross_equal_amounts(self):
        self.portfolio.order_queue.append(Market(True, 1000, "", "EUR_USD"))
        self.message_broker.on_next(Tick(Candle(1, 1, 1, 1, 1), 'H', datetime.now(), 'EUR_USD'))
        self.portfolio.order_queue.append(Market(False, -1000, "", "EUR_USD"))
        self.message_broker.on_next(Tick(Candle(1, 1, 1, 1, 1), 'H', datetime.now(), 'EUR_USD'))
        self.assertEqual(len(self.portfolio.order_queue), 0)
        self.assertEqual(len(self.portfolio.active_orders['EUR_USD']), 0)

    def test_cross_different_amounts_buy(self):
        self.portfolio.order_queue.append(Market(True, 1000, "", "EUR_USD"))
        self.message_broker.on_next(Tick(Candle(1, 1, 1, 1, 1), 'H', datetime.now(), 'EUR_USD'))
        self.portfolio.order_queue.append(Market(False, -500, "", "EUR_USD"))
        self.message_broker.on_next(Tick(Candle(1, 1, 1, 1, 1), 'H', datetime.now(), 'EUR_USD'))
        self.assertEqual(len(self.portfolio.order_queue), 0)
        self.assertEqual(len(self.portfolio.active_orders['EUR_USD']), 1)
        self.assertEqual(self.portfolio.active_orders['EUR_USD'][0].quantity, 500)

    def test_cross_different_amounts_sell(self):
        self.portfolio.order_queue.append(Market(True, 1000, "", "EUR_USD"))
        self.message_broker.on_next(Tick(Candle(1, 1, 1, 1, 1), 'H', datetime.now(), 'EUR_USD'))
        self.portfolio.order_queue.append(Market(False, -2000, "", "EUR_USD"))
        self.message_broker.on_next(Tick(Candle(1, 1, 1, 1, 1), 'H', datetime.now(), 'EUR_USD'))
        self.assertEqual(len(self.portfolio.order_queue), 0)
        self.assertEqual(len(self.portfolio.active_orders['EUR_USD']), 1)
        self.assertEqual(self.portfolio.active_orders['EUR_USD'][0].quantity, -1000)

