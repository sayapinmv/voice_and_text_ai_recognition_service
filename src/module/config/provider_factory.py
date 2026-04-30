from abc import ABC, abstractmethod

from src.module.config.provider import ConfigProvider, YamlProvider, EnvProvider


class ConfigProviderFactory(ABC):

    @abstractmethod
    def create(self, provider_name: str, file_path: str) -> ConfigProvider: pass


CONFIG_PROVIDERS_REGISTRY = {
    'yaml': YamlProvider,
    'yml': YamlProvider,
    'env': EnvProvider
}


class ConfigProviderFactoryImpl(ConfigProviderFactory):

    @classmethod
    def create(cls, provider_name: str, file_path: str) -> ConfigProvider:
        if provider_name not in CONFIG_PROVIDERS_REGISTRY:
            raise KeyError(f"Invalid provider_name '{provider_name}'. "
                           f"Valid providers names in CONFIG_PROVIDERS_REGISTRY: {CONFIG_PROVIDERS_REGISTRY.keys()}")

        provider = CONFIG_PROVIDERS_REGISTRY[provider_name]
        return provider(file_path)
