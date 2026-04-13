from pydantic import SecretStr, Field, BaseModel
from pydantic_settings import SettingsConfigDict
from typing import Literal, Any


class BaseAIModel(BaseModel):
    transcriptions_dirpath: str
    origins_dirpath: str
    model_settings: dict[str, Any]


class TextToSpeechAIModel(BaseAIModel):
    pass


class SpeechToTextAIModel(BaseAIModel):
    pass


class AIModels(BaseModel):
    speech_to_text: SpeechToTextAIModel = None
    text_to_speech: TextToSpeechAIModel = None


class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int = Field(8080, gt=0, le=65535)
    mode: Literal['DEV', 'PROD'] = Field('DEV')


class PerovskitePostgresDev(BaseModel):
    db_name: SecretStr
    user: SecretStr
    password: SecretStr
    host: str = "127.0.0.1"
    port: int = Field(5432, gt=0, le=65535)

    @property
    def connection_string(self) -> str:
        return (f"postgresql+psycopg2://{self.user.get_secret_value()}:{self.password.get_secret_value()}@"
                f"{self.host}:{self.port}/{self.db_name.get_secret_value()}")


class LoggingConfig(BaseModel):
    std_logger: dict = None


class AppConfig(BaseModel):
    ai_models: AIModels = None
    server: ServerConfig = None
    pg_perovskite_dev: PerovskitePostgresDev = None
    logging: LoggingConfig = None
