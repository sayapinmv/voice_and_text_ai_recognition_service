from abc import abstractmethod, ABC
from typing import Any, IO

from src.module.service.file_storage.disk_storage.service import DiskFileStorageService
from src.module.entity.transcription_entity import TranscriptionEntity
from src.module.logger.logger import Logger


class RecognitionService(ABC):

    def __init__(self,
                 default_settings: dict[str, Any],
                 origin_storage: DiskFileStorageService,
                 transcriptions_storage: DiskFileStorageService,
                 logger: Logger):

        self.default_settings = default_settings
        self.origin_storage = origin_storage
        self.transcriptions_storage = transcriptions_storage
        self.logger = logger

    @abstractmethod
    def create_transcription(self, filename: str, file: IO, model_settings: dict[str, Any] = None) -> TranscriptionEntity: pass
