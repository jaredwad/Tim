from rx.subjects import Subject

from Events.Indicator import Indicator
from Events.Tick import Tick


class Breakout:
    def __init__(self, message_broker: Subject, length: int = 5):
        self.name = 'Breakout'
        self.broker = message_broker
        self.data = dict()
        self.length = length

        tick = self.broker.filter(lambda x: x.type == 'TICK')
        tick.filter(lambda x: x.granularity == 'H').subscribe(self.tick)

    def tick(self, tick: Tick):
        instrument = tick.instrument

        if instrument not in self.data:
            self.data[instrument] = []

        if len(self.data[instrument]) >= self.length:
            self.send_signal(tick.candle.close, instrument)

        self.data[instrument].append(tick.candle.close)

        if len(self.data[instrument]) > self.length:
            self.data[instrument][:1] = []

    def send_signal(self, close_price, instrument: str):
        indicator = None

        if close_price > max(self.data[instrument]):
            indicator = Indicator(self.name, instrument, True)  # True for up
        elif close_price < min(self.data[instrument]):
            indicator = Indicator(self.name, instrument, False)  # False for down
        else:
            return None

        self.broker.on_next(indicator)
