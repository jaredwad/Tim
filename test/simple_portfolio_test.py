import unittest
from datetime import datetime

from rx.subjects import Subject

from Events.Candle import Candle
from Events.Market import Market
from Events.Tick import Tick
from MessageBroker.MessageBroker import MessageBroker
from Portfolio.Portfolio import Portfolio
from Portfolio.SimplePortfolio import SimplePortfolio


class SimplePortfolioTest(unittest.TestCase):
    def setUp(self):
        self.initial_funds = 100000
        self.message_broker = MessageBroker()
        self.portfolio = SimplePortfolio(self.message_broker, initial_funds=self.initial_funds)

    def test_adds_order(self):
        self.message_broker.submit_event(Market(True, 1000, "", "EUR_USD"))
        self.message_broker.submit_event(Candle(1, 1, 1, 1, 1, datetime.now()))
        self.assertEqual(len(self.portfolio.open_queue), 0)
        self.assertEqual(len(self.portfolio.current_holdings), 1)

    def test_stop_loss(self):
        self.message_broker.submit_event(Market(True, 1000, "", "EUR_USD", stop_loss=.1))
        self.message_broker.submit_event(Candle(1, 1, 1, 1, 1, datetime.now()))
        self.message_broker.submit_event(Candle(1, 1, 1, .9, 2, datetime.now()))
        self.message_broker.submit_event(Candle(.9, 1, 1, 1, 2, datetime.now()))
        self.assertEqual(len(self.portfolio.current_holdings), 0)
        self.assertEqual(self.portfolio.account_funds, self.initial_funds - 1000 * .1)

    def test_trailing_stop_loss(self):
        self.message_broker.submit_event(Market(True, 1000, "", "EUR_USD", stop_loss=.1, is_trailing_stop=True))
        self.message_broker.submit_event(Candle(1, 1, 1, 1, 1, datetime.now()))
        self.message_broker.submit_event(Candle(1, 1, 1, 1.1, 2, datetime.now()))
        self.message_broker.submit_event(Candle(1, 1, 1, 1, 1, datetime.now()))
        self.message_broker.submit_event(Candle(1, 1, 1, 1, 2, datetime.now()))
        self.assertEqual(len(self.portfolio.current_holdings), 0)
        self.assertEqual(self.portfolio.account_funds, self.initial_funds)

    def test_take_profit(self):
        self.message_broker.submit_event(Market(True, 1000, "", "EUR_USD", take_profit=.1))
        self.message_broker.submit_event(Candle(1, 1, 1, 1, 1, datetime.now()))
        self.message_broker.submit_event(Candle(1, 1, 1, 1.1, 1, datetime.now()))
        self.message_broker.submit_event(Candle(1.1, 1, 1, 1, 1, datetime.now()))
        self.assertEqual(len(self.portfolio.current_holdings), 0)
        self.assertEqual(self.portfolio.account_funds, self.initial_funds + 1000 * .1)


