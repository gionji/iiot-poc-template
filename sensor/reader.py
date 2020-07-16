from abc import abstractmethod, ABC
from random import randrange


class Reader(ABC):

    @abstractmethod
    def read(self):
        pass


class DummyReader(Reader):

    def __init__(self, key):
        self.key = key

    def read(self):
        return randrange(1, 100)
