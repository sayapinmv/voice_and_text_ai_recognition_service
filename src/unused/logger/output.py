from abc import ABC, abstractmethod

FILE_OUTPUT = 'file_output'
STDOUT_OUTPUT = 'stdout_output'

LEVELS = {
    'DEBUG':    1,
    'INFO':     2,
    'WARNING':  3,
    'ERROR':    4,
    'CRITICAL': 5
}


class LogOutput(ABC):
    def __init__(self, name: str, level: str, log_format: str):
        if level not in LEVELS:
            raise KeyError(f"unknown level: '{level}'")

        self.level = int(LEVELS[level])
        self.name = name
        self.log_format = log_format

    @abstractmethod
    def write(self, formatted_message: str): pass

    @abstractmethod
    def close(self): pass