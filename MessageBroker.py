from rx import Observable, Observer
from rx.subjects import Subject, BehaviorSubject


class MessageBroker:
    def __init__(self):
        self.subject = Subject()

    def emit(self, value):
        self.subject.on_next(value)

    def get_observable(self):
        return self.subject
