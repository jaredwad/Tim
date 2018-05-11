import time
from datetime import datetime, timedelta

from rx import Observable, AnonymousObservable
from rx.concurrency import timeout_scheduler
from rx.disposables import SerialDisposable
from rx.internal import extensionmethod
from rx.subjects import Subject


class Turtle:
    def __init__(self, queue: Subject):
        self.queue = queue

    def attach_to_queue(self):
        self.queue.buffer_while(lambda x, y: x.time.day == y.time.day).buffer(20,1)\
            .map(lambda x: float(sum(x))/max(len(x),1)).subscribe(print)


class item:
    def __init__(self, id, time):
        self.id = id
        self.time = time

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

def print_ids(x):
    for p in x:
        print(p.id)
    print()

queue = Subject()

queue.buffer_while(lambda x, y: x.time.day == y.time.day).map(lambda x: [y.id for y in x]).map(lambda x: sum(x)).buffer_with_count(3,1).subscribe(print)

#dist.subscribe(print)


queue.on_next(item(1, datetime.today() - timedelta(5)))
queue.on_next(item(2, datetime.today() - timedelta(5)))
queue.on_next(item(3, datetime.today() - timedelta(5)))
queue.on_next(item(3, datetime.today() - timedelta(4)))
queue.on_next(item(3, datetime.today() - timedelta(4)))
queue.on_next(item(4, datetime.today() - timedelta(3)))
queue.on_next(item(5, datetime.today() - timedelta(3)))
queue.on_next(item(1, datetime.today() - timedelta(2)))
queue.on_next(item(2, datetime.today() - timedelta(2)))
queue.on_next(item(3, datetime.today() - timedelta(2)))
queue.on_next(item(3, datetime.today() - timedelta(2)))
queue.on_next(item(3, datetime.today() - timedelta(2)))
queue.on_next(item(4, datetime.today() - timedelta(1)))
queue.on_next(item(5, datetime.today() - timedelta(1)))
queue.on_next(item(6, datetime.now()))
queue.on_completed()