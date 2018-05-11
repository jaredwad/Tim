from rx.subjects import Subject
from sklearn.externals import joblib

from Events.Close import Close
from Events.Fill import Fill
from Events.Market import Market
from Events.Tick import Tick
import pandas as pd
import numpy as np


class PricePredictor:
    def __init__(self, classifier_filename: str, message_broker: Subject, instrument: str = 'EUR_USD'):
        self.name = 'PricePredictor'
        self.broker = message_broker
        tick = self.broker.filter(lambda x: x.type == 'TICK')
        tick.filter(lambda x: x.granularity == 'H').subscribe(self.tick_hour)

        self.broker.filter(lambda x: x.type == 'FILL').filter(lambda x: x.strategy_name == self.name)\
            .subscribe(self.entered)

        self.broker.filter(lambda x: x.type == 'CLOSE').filter(lambda x: x.strategy_name == self.name) \
            .subscribe(self.exited)

        self.clf = joblib.load(classifier_filename)
        self.instrument = instrument
        self.current_direction = None
        self.current_positions = []
        self.predictions = []
        self.prediction_length = 5  # How far in the future we're predicting

    def in_market(self):
        return len(self.current_positions) > 0

    def tick_hour(self, event: Tick):
        if not self.current_direction:
            direction = self.should_enter(event.candle)
            if direction is not None:
                self.enter(direction)
        else:
            direction = self.should_exit(event.candle)
            if direction is not None:
                self.exit(direction)

    def should_enter(self, candle):
        pred = self.predict_price(candle=candle)
        dif = pred - candle.close

        if abs(dif) > 0.0003:
            return "BUY" if dif > 0 else "SELL"
        return None

    def should_exit(self, candle):
        pred = self.predict_price(candle=candle)

        self.predictions.append(pred)
        self.predictions.pop(0)

        if self.current_direction == "BUY" and candle.close > max(self.predictions[1:]):
            return "SELL"
        elif self.current_direction == "SELL" and candle.close < min(self.predictions[1:]):
            return "BUY"
        return None

    def predict_price(self, candle):
        data = [candle.close, candle.high, candle.low, candle.open, candle.volume]
        return self.clf.predict(np.array(data).reshape(1, -1))[0]

    def enter(self, direction: str):
        print("Entering!!!")
        self.broker.on_next(Market(direction=direction == "BUY", quantity=1000, strategy_name=self.name, instrument=self.instrument))
        self.current_direction = direction

    def entered(self, fill_event: Fill):
        self.current_positions.append(fill_event)
        if not self.predictions:
            self.predictions = np.empty(self.prediction_length)
            self.predictions.fill(fill_event.close_price)
            self.predictions = self.predictions.tolist()

    def exit(self, direction):
        print("Exiting!!!")
        self.broker.on_next(Market(direction=direction == "BUY", quantity=1000, strategy_name=self.name, instrument=self.instrument))

    def exited(self, close_event: Close):
        self.current_positions = self.current_positions[1:]
        # TODO add support for multiple positions (The code below blows away everything)
        self.current_direction = None
        self.predictions = []
