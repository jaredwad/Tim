from rx import Observable, AnonymousObservable
from rx.concurrency import timeout_scheduler
from rx.disposables import SerialDisposable
from rx.internal import extensionmethod
from rx.subjects import Subject

from Events.DataReady import DataReady
from Events.Indicator import Indicator
from Events.Candle import Candle
from Events.Market import Market


class MessageBroker:
    def __init__(self):
        self.subject = Subject()

    def submit_event(self, event):
        self.subject.on_next(event)

    def get_ticks_hourly(self):
        return self.subject

    def get_candles(self):
        return self.subject.filter(lambda x: x.type == Candle.get_name())

    def get_indicator(self):
        return self.subject.filter(lambda x: x.type == Indicator.get_name())

    def get_data_ready(self):
        return self.subject.filter(lambda x: x.type == DataReady.get_name())

    def get_market(self):
        return self.subject.filter(lambda x: x.type == Market.get_name())

@extensionmethod(Observable)
def buffer_while(self, condition, scheduler=None):
    source = self
    scheduler = scheduler or timeout_scheduler

    def subscribe(observer):
        cancelable = SerialDisposable()
        buffer=list()

        def on_next(x):
            nonlocal buffer
            if len(buffer) != 0 and not condition(x, buffer[-1]):
                observer.on_next(buffer)
                buffer = [x]
            else:
                buffer.append(x)

        def on_completed():
            observer.on_next(buffer)
            observer.on_completed()

        cancelable.disposable = scheduler.schedule(on_next)
        return source.subscribe(on_next, observer.on_error, on_completed)

    return AnonymousObservable(subscribe)
