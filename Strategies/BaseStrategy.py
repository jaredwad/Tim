from abc import ABC, abstractmethod


class BaseStrategy(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def do_something(self):
        pass