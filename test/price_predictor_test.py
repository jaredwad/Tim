import unittest
from unittest.mock import MagicMock

from rx.subjects import Subject

from Events.Candle import Candle
from Events.Tick import Tick
from Strategies.PricePredictor import PricePredictor


class ExecutorTest(unittest.TestCase):
    def setUp(self):
        self.subject = Subject()
        self.predictor = PricePredictor('/Users/jared/Dev/Tim/research/linear_regressesor.pkl', self.subject)

    def test_buy(self):
        self.predictor.should_enter = MagicMock(return_value=True)
        self.predictor.buy = MagicMock()
        self.subject.on_next(Tick(Candle(open=1, high=1, low=1, close=1, volume=1), 'H', 1))
        self.predictor.should_enter.assert_called()
        self.predictor.buy.assert_called()
