from logging import config
import sys
import logging

from src.module.logger.std_logging.filter import ContextFilter
from src.module.logger.logger import Logger


class StdLogger(Logger):
    DEFAULT_LEVEL = logging.DEBUG
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
    DEFAULT_DATE_FMT = '%d-%m-%Y %H:%M:%S'

    def __init__(self, logger_config: dict = None):

        if logger_config is None:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(self.DEFAULT_LEVEL)

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.DEFAULT_LEVEL)

            formatter = logging.Formatter(self.DEFAULT_FORMAT, self.DEFAULT_DATE_FMT)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)

        else:
            config.dictConfig(logger_config)
            self.logger = logging.getLogger('root')

        self.logger.addFilter(ContextFilter())
        super().__init__(self.logger.name)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
