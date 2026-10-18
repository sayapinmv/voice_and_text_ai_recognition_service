from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Any, BinaryIO

from src.module.entities.file import FileEntity
from src.module.logger.logger import Logger
from src.module.service.file_storage.service_impl import FileStorageService

@dataclass
class Config:
    model_settings: dict[str, Any]
    default_transcription_settings: dict[str, Any]

@dataclass
class RecognitionDto:
    filename: str
    file: BinaryIO
    model_settings: dict[str, Any] = None

class RecognitionService(ABC):

    def __init__(self,
                 file_service: FileStorageService,
                 logger: Logger):

        self.file_service = file_service
        self.logger = logger

    @abstractmethod
    def set_up_model(self, settings: Any): pass

    @abstractmethod
    def set_up_transcription_settings(self, model_settings: Any): pass

    @abstractmethod
    def create_transcription(self, recognition_dto: RecognitionDto) -> FileEntity: pass
