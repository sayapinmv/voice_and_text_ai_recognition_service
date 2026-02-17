from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource
from pydantic import SecretStr, Field, BaseModel
from typing import Literal
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.parent.absolute()
ENV_FILE_PATH = ROOT_DIR / ".env"
YAML_FILE_PATH = ROOT_DIR / "config.yaml"
ENV_FILE_ENCODING = "utf-8"
YAML_FILE_ENCODING = "utf-8"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding=ENV_FILE_ENCODING,
        case_sensitive=False,
    )


class PerovskitePostgresDev(Settings):
    model_config = SettingsConfigDict(env_prefix='PG_PEROVSKITE_DEV_')

    db_name: SecretStr
    user: SecretStr
    password: SecretStr
    host: SecretStr = "127.0.0.1"
    port: int = Field(5432, gt=0)


class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int = Field(5432, gt=0)
    mode: Literal[
        'DEV',
        'PROD'
    ] = Field('DEV')


class LoggingConfig(BaseModel):
    std_logger: dict = None


class Config(BaseSettings):
    model_config = SettingsConfigDict(yaml_file=YAML_FILE_PATH,
                                      yaml_file_encoding=YAML_FILE_ENCODING)

    perovskite_pg_dev: PerovskitePostgresDev = Field(default_factory=PerovskitePostgresDev)
    server: ServerConfig
    logging: LoggingConfig

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (YamlConfigSettingsSource(settings_cls),)

    @classmethod
    def load(cls) -> "Config":
        return cls()
