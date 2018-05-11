import unittest

from Indicator.Candle import Candle
from Events.Market import Market
from Events.Tick import Tick
from Executor import Executor


class ExecutorTest(unittest.TestCase):
    def setUp(self):
        self.executor = Executor()

    def test_should_enter(self):
        self.assertFalse(self.executor.in_market())
        self.executor.consume(Market("BUY", 1000))
        self.executor.consume(Tick(Candle(1, 1, 1, 1), 'H'))
        self.assertTrue(self.executor.in_market())

    def test_should_exit(self):
        self.executor.consume(Market("BUY", 1000))
        self.executor.consume(Tick(Candle(1, 1, 1, 1), 'H'))
        self.assertTrue(self.executor.in_market())
        self.executor.consume(Market("SELL", 1000))
        self.executor.consume(Tick(Candle(1, 1, 1, 1), 'H'))
        self.assertFalse(self.executor.in_market())

        # Now test the opposite
        self.executor.consume(Market("SELL", 1000))
        self.executor.consume(Tick(Candle(1, 1, 1, 1), 'H'))
        self.assertTrue(self.executor.in_market())
        self.executor.consume(Market("BUY", 1000))
        self.executor.consume(Tick(Candle(1, 1, 1, 1), 'H'))
        self.assertFalse(self.executor.in_market())

    def test_should_calculate_earnings(self):
        self.executor.account_balance = 1000
        self.executor.consume(Market("BUY", 1000))
        self.executor.consume(Tick(Candle(1, 1, 1, 1), 'H'))
        self.executor.consume(Market("SELL", 1000))
        self.executor.consume(Tick(Candle(2, 2, 2, 2), 'H'))
        self.assertEqual(self.executor.account_balance, 2000)
