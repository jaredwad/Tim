from DataHandler.DataRepository import DataRepository
from Events.DataReady import DataReady
from Indicator.Indicators import EMA, RSI
from MessageBroker.MessageBroker import MessageBroker


class HLHB:
    def __init__(self, data_repo: DataRepository, message_broker: MessageBroker, long=10, short=5
                 , rsi_length=10, rsi_val=50., trailing_stop=50., take_profit=200.):
        self.data_repo = data_repo
        self.data_repo.add_indicator(EMA, [long])
        self.data_repo.add_indicator(EMA, [short])
        self.data_repo.add_indicator(RSI, [rsi_length])

        self.long_name = 'ema_' + str(long)
        self.short_name = 'ema_' + str(short)
        self.rsi_name = 'rsi_' + str(rsi_length)
        self.rsi_val = rsi_val

        self.trailing_stop = trailing_stop
        self.take_profit = take_profit

        self.in_market = None

        self.message_broker = message_broker

        self.message_broker.get_data_ready().subscribe(self.handle_tick)

    def handle_tick(self, event: DataReady):
        data = self.data_repo.get_data(1)

        if self.in_market is None:
            self.handle_enter(data)
        else:
            self.handle_exit(data)

    def handle_enter(self, data):
        long = data[self.long_name]
        short = data[self.short_name]
        rsi = data[self.rsi_name]

        if short > long and rsi > self.rsi_val:
            self.buy()
        elif short < long and rsi < self.rsi_val:
            self.sell()

    def handle_exit(self, data):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

    def exit(self):
        pass