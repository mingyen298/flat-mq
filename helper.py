from enum import Enum, auto


class Constants:
    _instance = None
    BrokerURL = "0.0.0.0"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass


class MQPacketStatus(int, Enum):
    Default = 0
    Sending = auto()
    Processing = auto()
    Responding = auto()
    Finished = auto()
