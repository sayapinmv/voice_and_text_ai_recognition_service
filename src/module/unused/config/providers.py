import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from abc import ABC, abstractmethod
from yaml import full_load
from pathlib import Path
import re
import dotenv
import os


class ConfigLoader(ABC):
    pass

class EnvVarsResolver(ABC):
    pass

class ConfigProvider(ABC):

class ConfigProvider(ABC):

    def __init__(self, file_path: str | Path, encoding: str = 'utf-8'):
        if file_path == '' or file_path is None:
            raise ValueError("missed required ConfigProvider init param 'file_path'.")

        self.file_path = Path(file_path)
        self.encoding = encoding

        if not self.file_path.exists():
            raise FileExistsError(f"YamlProvider by path '{self.file_path}' is not exist.")


    @abstractmethod
    def load(self) -> dict: pass

    @abstractmethod
    def get_value(self, key) -> str: pass


ENV_FILE_PATH = './.env'
ENV_VAR_PATTERN = r'\$\{([^}]+)\}'


class YAMLConfig(ConfigProvider):

    def __init__(self, file_path: str, encoding: str):
        super().__init__(file_path, encoding)
        self.yaml_cfg = None

    def load(self) -> dict:
        with open(self.file_path, mode='r', encoding=self.encoding) as yaml_cfg_file:
            self.yaml_cfg = yaml.full_load(yaml_cfg_file)
            return self.yaml_cfg

    def get_value(self, key) -> str:
        if key in self.yaml_cfg:
            return ''
        else:
            raise KeyError(f"No value(-s) for key '{key}' in YamlProvider config data.")

    def _check_env_var(self, cfg_frame: dict):
        for key, val in dict(cfg_frame).items():
            if isinstance(val, dict):
                self._check_env_var(val)
            else:
                match = re.search(ENV_VAR_PATTERN, str(val))
                if bool(match):
                    env_var_val = super().settings.
                    cfg_frame[key] = env_var_val

cfg1 = YAMLConfig('asfd.yaml', 'utf-8')
cfg2 = YAMLConfig(file_path='asfd.yaml', encoding='utf-8')


#
#
# class EnvProvider(ConfigProvider):
#
#     def __init__(self, cfg_path: str):
#         super().__init__(cfg_path)
#         self.cfg_path = cfg_path
#
#     def load(self):
#         dotenv.load_dotenv(self.cfg_path)
#
#     def get_value(self, key: str) -> str:
#         return os.getenv(key)
#
#
# class YAMLProvider(ConfigProvider):
#
#     def __init__(self, cfg_path: str, env_provider: EnvProvider):
#         super().__init__(cfg_path)
#         self.cfg_path = cfg_path
#         self.env_provider = env_provider
#         self._cfg_data = {}
#
#     def load(self):
#         with open(self.env_provider.get_value('CONFIG_YAML'), 'r', encoding='utf-8') as f:
#             cfg_data = full_load(f)
#             self._check_env_var(cfg_data)
#             self._cfg_data = cfg_data
#
#     def get_value(self, key) -> str:
#         return self._cfg_data[key]
#
#     def _check_env_var(self, cfg_data: dict):
#         for key, val in dict(cfg_data).items():
#             if isinstance(val, dict):
#                 self._check_env_var(val)
#             else:
#                 match = re.search(ENV_VAR_PATTERN, str(val))
#                 if bool(match):
#                     env_var_val = self.env_provider.get_value(match.groups()[0])
#                     cfg_data[key] = env_var_val
