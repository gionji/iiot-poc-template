import json
from abc import abstractmethod, ABC
from datetime import datetime
from random import randrange


class SensorValue:
    def __init__(self, key, value, timestamp):
        self.key = key
        self.value = value
        self.timestamp = timestamp

    def format(self):
        return json.dumps({
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp
        })


class Reader(ABC):

    @abstractmethod
    def read(self) -> SensorValue:
        pass


class DummyReader(Reader):

    def __init__(self, key):
        self.key = key

    def read(self) -> SensorValue:
        return SensorValue(self.key, randrange(10, 100), int(datetime.now().timestamp()))


# Opc reader


# Opc callback reader


# Modbus reader


# I2C Reader
