from src.module.unused.config.providers import ConfigProvider, EnvProvider
from src.module.unused.config.settings import FieldSetting


class Config:

    def __init__(self, provider: ConfigProvider = EnvProvider):
        self.provider = provider

    def field(self, key: str, field_setting: FieldSetting = None):
        val = self.provider.get_value(key)

        if field_setting is not None:
            val = field_setting.setting_value(val)

        return val


class ServerConf(Config):

    @property
    def port(self):
        return super().field("port")

    @property
    def host(self):
        return super().field("host")


class DataSources(Config):

    def __init_(self, provider=None):
        super().__init__(provider)
