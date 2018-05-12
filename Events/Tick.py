import datetime

from Events.Candle import Candle


class Tick:
    def __init__(self, candle: Candle, granularity: str, date: datetime, instrument: str):
        self.type = 'TICK'
        self.candle = candle
        self.granularity = granularity
        self.date = date
        self.instrument = instrument
