from abc import ABC, abstractmethod
from yaml import full_load
import dotenv

DEFAULT_FILE_MODE = 'r'
DEFAULT_FILE_ENCODING = 'utf-8'


class ConfigProvider(ABC):

    def __init__(
            self,
            provider_name: str,
            file_path: str,
            encoding: str = DEFAULT_FILE_ENCODING,
            mode: str = DEFAULT_FILE_MODE
    ):
        self._provider_name = provider_name
        self._file_path = file_path
        self._encoding = encoding
        self._mode = mode

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def mode(self) -> str:
        return self._mode

    @abstractmethod
    def load(self) -> dict: pass


class YamlProvider(ConfigProvider):

    def __init__(self, file_path: str,
                 encoding: str = DEFAULT_FILE_ENCODING,
                 mode: str = DEFAULT_FILE_MODE):

        super().__init__('yaml', file_path, encoding, mode)

    def load(self) -> dict:
        with open(self.file_path, mode=self.mode, encoding=self.encoding) as conf_file:
            return full_load(conf_file)


class EnvProvider(ConfigProvider):

    def __init__(self, file_path: str,
                 encoding: str = DEFAULT_FILE_ENCODING,
                 mode: str = DEFAULT_FILE_MODE):

        super().__init__('env', file_path, encoding, mode)

    def load(self) -> dict:
        return dotenv.dotenv_values(self.file_path, encoding=self.encoding)
