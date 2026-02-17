from colorama import Fore, Style
from logging import Formatter
import logging


class ColoredFormatter(Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        if record.levelno in self.COLORS:
            record.levelname = (f"{self.COLORS[record.levelno]}"
                                f"{record.levelname}{Style.RESET_ALL}")

            record.message = (f"{self.COLORS[record.levelno]}"
                              f"{record.msg}{Style.RESET_ALL}")

        return super().format(record)


class StructuredFormatter(Formatter):

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        result = (f"timestamp={self.formatTime(record)} level={record.levelname} "
                  f"logger={record.name} msg={record.getMessage()}")

        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith('_'):
                result += f" {key}={value}"

        return result
