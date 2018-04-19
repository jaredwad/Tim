import unittest
from datetime import datetime

import numpy.random as nprnd

from Candle import Candle
from DataImporter import CSVDataImporter
from ShortBreakout import ShortBreakout


class ShortBreakoutTest(unittest.TestCase):
    def setUp(self):
        self.breakout = ShortBreakout()

        self.importer = CSVDataImporter('/Users/jared/Dev/Tim/data/EUR_USD.csv')
        self.prices = []
        for index, row in self.importer.data.iterrows():
            self.prices.append(row['close'])

    def test_tick_day(self):
        data = nprnd.ranf(1000)
        for item in data:
            self.breakout.tick_day(item)

        self.assertListEqual(data[-20:].tolist(), self.breakout.data)

    def test_should_enter(self):
        self.breakout.data = self.prices[:20]
        self.breakout.tick_hour(1.18615)
        self.assertTrue(self.breakout.should_enter() == "BUY")
        self.breakout.tick_hour(1.17658)
        self.assertTrue(self.breakout.should_exit())
        self.breakout.tick_hour(1.18615)
        self.assertTrue(self.breakout.should_enter() is None)

    def test_num_breakouts(self):
        count = 0
        skip = False
        for i in range(len(self.prices) - 21):
            if skip:
                if self.prices[i + 11] < min(self.prices[i:i + 10]):
                    skip = False
                continue

            if self.prices[i+21] > max(self.prices[i:i+20]):
                skip = True
                count += 1
        print(count)
