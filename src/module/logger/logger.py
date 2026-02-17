from abc import ABC, abstractmethod


class Logger(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def debug(self, msg: str, *args, **kwargs): pass

    @abstractmethod
    def info(self, msg: str, *args, **kwargs): pass

    @abstractmethod
    def warning(self, msg: str, *args, **kwargs): pass

    @abstractmethod
    def error(self, msg: str, *args, **kwargs): pass

    @abstractmethod
    def critical(self, msg: str, *args, **kwargs): pass
