import pandas as pd
import numpy as np
from datetime import datetime

from Events.DataReady import DataReady
from Indicator.Candle import Candle
from Indicator.IndicatorBus import IndicatorBus
from Indicator.Indicators import MA, EMA, MOM, BBANDS
from MessageBroker.MessageBroker import MessageBroker


class DataRepository:
    def __init__(self, indicator_bus: IndicatorBus, message_broker: MessageBroker):
        self.data = pd.DataFrame()
        self.indicators_bus = indicator_bus

        self.message_broker = message_broker
        self.message_broker.get_candles().subscribe(self.handle_tick)

    def get_data(self, rows_to_return=10):
        return self.data[:-rows_to_return, :]

    def handle_tick(self, candle: Candle):
        d = {'open': candle.open, 'high': candle.high, 'low': candle.low, 'close': candle.close
            , 'volume': candle.volume}
        temp = pd.DataFrame(data=d, index=[candle.time], dtype=np.float32)
        self.data = self.data.append(temp)

        self.data = self.indicators_bus.handle_ticks(self.data)

        self.message_broker.submit_event(DataReady())

    def add_indicator(self, indicator, params):
        self.indicators_bus.add_indicator(indicator, params)


if __name__ == '__main__':
    ib = IndicatorBus()

    ib.add_indicator(MA, [2])
    ib.add_indicator(EMA, [2])
    ib.add_indicator(MOM, [2])
    ib.add_indicator(BBANDS, [2])


    dr = DataRepository(ib)

    dr.handle_tick(Candle(1.0, 1, 1, 1.0, 1, datetime.now()))
    dr.handle_tick(Candle(1.1, 1, 1, 1.1, 1, datetime.now()))
    dr.handle_tick(Candle(1.2, 1, 1, 1.2, 1, datetime.now()))
    dr.handle_tick(Candle(1.3, 1, 1, 1.3, 1, datetime.now()))
    dr.handle_tick(Candle(1.4, 1, 1, 1.4, 1, datetime.now()))
    dr.handle_tick(Candle(1.5, 1, 1, 1.5, 1, datetime.now()))
    dr.handle_tick(Candle(1.6, 1, 1, 1.6, 1, datetime.now()))
    dr.handle_tick(Candle(1.7, 1, 1, 1.7, 1, datetime.now()))
    dr.handle_tick(Candle(1.8, 1, 1, 1.8, 1, datetime.now()))

    with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
        print(dr.data.to_string())
