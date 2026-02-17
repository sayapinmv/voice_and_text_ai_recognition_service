import src.module.logger.logger as log
import logging
import sys
from datetime import datetime
from pathlib import Path
import uuid


FILE_TEMPLATE_VARS = {
    'uuid': str(uuid.uuid4()),
    'date': datetime.now().strftime('%Y%m%d'),
    'times': datetime.now().strftime('%H%M%S'),
    'datetime': datetime.now().strftime('%Y%m%d_%H%M%S'),
}

LOG_FORMAT = 'timestamp: {asctime}, name: {name}, level: [{levelname}], msg: {message}'


class FileOutput(log.LogOutput):

    def __init__(self,
                 level: str = "DEBUG",
                 mode: str = 'a',
                 encoding: str = 'utf-8',
                 filename_template: str = 'log_{uuid}.log',
                 log_file_dir: str = './log',
                 max_size: int = 1024 * 1024,
                 backups_count: int = 5,
                 file_template_vars: dict = None):

        super().__init__(log.FILE_OUTPUT, level, LOG_FORMAT)

        self.encoding = encoding
        self.format = LOG_FORMAT
        self._log_file_mode = mode

        self.filename_template = filename_template.removeprefix("/")
        self._log_dir_path = Path(log_file_dir.removesuffix("/"))
        self._max_size = max_size
        self._backups_count = backups_count
        self._file_template_vars = file_template_vars if file_template_vars is not None else {}

        self.log_file_path = Path()
        self._check_log_dir()
        self._create_log_filepath()

        self._log_file = None
        self._open_file()

    def write(self, formatted_message: str):
        # self._rotate_if_needed()
        self._log_file.write(formatted_message + '\n')
        self._log_file.flush()

    def close(self):
        if self._log_file and not self._log_file.closed:
            self._log_file.close()

    def _check_log_dir(self):
        self._log_dir_path.mkdir(parents=True, exist_ok=True)

    def _create_log_filepath(self):
        template_vars = {**FILE_TEMPLATE_VARS, **self._file_template_vars}

        try:
            filename = self.filename_template.format(**template_vars)
        except KeyError:
            raise KeyError

        self.log_file_path = Path(f'{self._log_dir_path}/{filename}')

    def _open_file(self):
        self._log_file = open(self.log_file_path, self._log_file_mode, encoding=self.encoding)

    # TODO working log rotation
    # def _rotate_if_needed(self):
    #     if self.log_file_path.exists() and self.log_file_path.stat().st_size > self._max_size:
    #         self.close()
    #
    #         for i in range(self._backups_count - 1, 0, -1):
    #             old_file = self.log_file_path.with_suffix(f'.log.{i}')
    #             new_file = self.log_file_path.with_suffix(f'.log.{i + 1}')
    #             if old_file.exists():
    #                 old_file.rename(new_file)
    #
    #         backup_file = self.log_file_path.with_suffix('.log.1')
    #         if self.log_file_path.exists():
    #             self.log_file_path.rename(backup_file)
    #
    #         self._open_file()

class StdoutOutput(log.LogOutput):
    def __init__(self,
                 level: str = "DEBUG"):

        super().__init__(log.STDOUT_OUTPUT, level, LOG_FORMAT)
        self.stream = sys.stdout

    def write(self, formatted_message: str):
        self.stream.write(formatted_message + '\n')
        self.stream.flush()

    def close(self):
        pass
