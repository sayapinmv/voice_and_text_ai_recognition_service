from datetime import datetime
import src.module.logger.logger as log
import logging
import uuid


class StdLogger(log.Logger):
    def __init__(self,
                 name: str = __name__,
                 *outputs: log.LogOutput):

        super().__init__(name)

        self.name = name
        self.outputs = list(outputs)

        self._logger = logging.getLogger(self.name)
        self._logger.handlers.clear()

    def _log(self, level: str, msg: str, *args, **kwargs):
        # frame = inspect.currentframe().f_back
        # file_info = inspect.getframeinfo(frame)

        for output in self.outputs:
            if log.LEVELS[level] >= output.level:
                # TODO log message without necessary dict

                log_msg_fields = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'level': f'[{level}]',
                    **kwargs
                }

                formatted_log_msg = ', '.join(f"{k}: {v}" for k, v in log_msg_fields.items())

                try:
                    output.write(formatted_log_msg)
                except KeyError:
                    fallback = f"{datetime.now()} [{level}] {formatted_log_msg}"
                    output.write(fallback)

    def debug(self, msg: str, *args, **kwargs):
        self._log('DEBUG', msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._log('INFO', msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._log('WARNING', msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._log('ERROR', msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._log('CRITICAL', msg, *args, **kwargs)


DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_LOG_FILE_TEMPLATE = 'log_{uuid}.log'
FORMAT_LITERAL = '{'

FORMATTERS = {
    "speech_to_text": {
        "format":  "{asctime}  {name} [{levelname}] {message}",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "json": {
        "format":  "",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
}

FILE_TEMPLATE_VARS = {
    'uuid': str(uuid.uuid4()),
    'date': datetime.now().strftime('%Y%m%d'),
    'times': datetime.now().strftime('%H%M%S'),
    'datetime': datetime.now().strftime('%Y%m%d_%H%M%S'),
}


def get_log_level(level: str = DEFAULT_LOG_LEVEL):
    try:
        log_level = log.LEVELS[level.upper()]
    except KeyError:
        raise KeyError

    return log_level


def get_log_format(log_format: str = DEFAULT_LOG_FORMAT, formatter_literal: str = DEFAULT_LOG_LITERAL):
    try:
        log_formatter = logging.Formatter(log_format, style=formatter_literal)
    except Exception as exc:
        raise f'failed parsing log_format. err: {exc}'

    return log_formatter


class FileOutput:

    def __init__(self, level: str = DEFAULT_LOG_LEVEL,
                 log_format: str = DEFAULT_LOG_FORMAT,
                 formatter_literal: str = DEFAULT_LOG_LITERAL,
                 filename_template: str = '',
                 mode: str = 'a',
                 encoding: str = 'utf-8',
                 max_size: int = 5,
                 backups_count: int = 5):

        self.file_handler = RotatingFileHandler(filename_template, mode, max_size, backups_count, encoding)
        self.file_handler.setLevel(get_log_level(level))
        self.file_handler.setFormatter(get_log_format(log_format, formatter_literal))

    def _create_filename(self):
        pass


class ConsoleOutput:

    def __init__(self, level: str = DEFAULT_LOG_LEVEL,
                 stream=sys.stdout,
                 log_format: str = DEFAULT_LOG_FORMAT,
                 formatter_literal: str = DEFAULT_LOG_LITERAL):

        self.console_handler = logging.StreamHandler(stream)
        self.console_handler.setLevel(get_log_level(level))
        self.console_handler.setFormatter(get_log_format(log_format, formatter_literal))

class StdLogger: #(logger.Logger):

    def __init__(self, name: str = __name__,
                 level: str = DEFAULT_LOG_LEVEL,
                 handlers: list[logging.Handler] = None):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(get_log_level(level))

        if handlers is not None:
            for handler in handlers:
                self.logger.addHandler(handler)
        else:
            self.logger.addHandler(ConsoleOutput().console_handler)

    def _log(self, level: int, msg: str, *args, **kwargs):
        if level < self.logger.level:
            return

        try:
            # Пропускаем 2 фрейма: 0 - этот метод, 1 - debug/info/error, 2 - код пользователя
            frame = sys._getframe(2)
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            func_name = frame.f_code.co_name
        except (AttributeError, ValueError):
            filename = "unknown"
            lineno = 0
            func_name = "unknown"

        formatted_message = msg

        for handler in self.logger.handlers:
            if args:
                try:
                    if '{' in msg and '}' in msg:
                        formatted_message = msg.format(*args)
                    else:
                        formatted_message = msg % args
                except (TypeError, ValueError, KeyError, IndexError):
                    formatted_message = f"{msg} | args: {args}"

            #extra_data = {**self.defaults, **kwargs}

            record = self.logger.makeRecord(
                name=self.logger.name,
                level=level,
                fn=filename,
                lno=lineno,
                msg=formatted_message,
                args=(),
                exc_info=None,
                func=func_name,
                # extra=extra_data,
                sinfo=None
            )

            handler.handle(record)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg)

    def info(self, msg: str, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)
        # self.logger.info(msg)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg)
