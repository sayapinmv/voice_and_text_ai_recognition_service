from abc import ABC, abstractmethod
from typing import Any
import os
import re

from src.module.config.provider import ConfigProvider
from src.module.config.model import AppConfig


class ConfigBuilder(ABC):

    # def __init__(self, provider_factory: ConfigProviderFactory):
    #     self._provider_factory = provider_factory
    #
    # @property
    # def provider_factory(self):
    #     return self._provider_factory

    @abstractmethod
    def add_provider(self, provider: ConfigProvider) -> 'ConfigBuilder': pass

    @abstractmethod
    def build(self) -> AppConfig: pass


class ConfigBuilderImpl(ConfigBuilder):
    ENV_VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')

    _providers: dict[str, ConfigProvider] = {}
    _env_config = {}
    _configs = {}

    def add_provider(self, provider: ConfigProvider) -> ConfigBuilder:
        self._providers[provider.provider_name] = provider
        return self

    def build(self) -> AppConfig:
        self._load_configs()
        return AppConfig().model_validate(self._configs)

    def _load_configs(self):
        if self._providers is None:
            self._configs['env'] = os.environ
            return
        else:
            if 'env' in self._providers:
                try:
                    self._env_config = self._providers['env'].load()
                except Exception as exc:
                    raise exc
                self._providers.pop('env')

            for name, provider in self._providers.items():
                try:
                    self._configs.update(**provider.load())
                except Exception as exc:
                    raise exc

                if self._env_config is not None:
                    self._resolve_env_vars(self._configs)

    def _resolve_env_vars(self, val) -> Any:

        if isinstance(val, dict):
            for k, v in dict(val).items():
                val[k] = self._resolve_env_vars(v)

        if isinstance(val, list):
            return [self._resolve_str(v) for v in val if isinstance(v, str)]

        if isinstance(val, str):
            return self._resolve_str(val)

        return val

    def _resolve_str(self, val: str) -> str:
        match = self.ENV_VAR_PATTERN.search(val)
        if match:
            env_var_key = match.group(1)
            if self._env_config is None:
                self._env_config = os.environ

            if env_var_key in self._env_config:
                return self._env_config[env_var_key]

        return val
