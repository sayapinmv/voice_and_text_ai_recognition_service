from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO, Any

from src.module.entities.file import FileEntity
from src.module.entities.transcription import TranscriptionType, TranscriptionEntity
from src.module.repository.transcription import TranscriptionRepository

from src.module.service.file_storage.service import FileStorageService
from src.module.service.recognition.service import RecognitionService
from src.module.logger.logger import Logger


@dataclass
class TranscriptionDto:
    filename: str
    file: BinaryIO
    type: TranscriptionType
    model_settings: dict[str, Any]

class TranscriptionService(ABC):

    def __init__(self,
                 recognition_services: dict[TranscriptionType, RecognitionService],
                 transcription_repo: TranscriptionRepository,
                 file_service: FileStorageService,
                 logger: Logger):

        self.recognition_services = recognition_services
        self.transcription_repo = transcription_repo
        self.file_service = file_service
        self.logger = logger

    @abstractmethod
    def get(self, id: int) -> TranscriptionEntity: pass

    @abstractmethod
    def create(self, transcription_dto: TranscriptionDto) -> TranscriptionEntity: pass

    @abstractmethod
    def remove(self, id: int): pass

    def get_origin_filepath(self, id: int) -> FileEntity:
        try:
            entity = self.transcription_repo.get_by_id(id)
        except Exception as exc:
            self.logger.error(f'Failed to get transcription entity for getting origin filepath: {exc}')
            raise RuntimeError('Failed to get transcription entity for getting origin filepath') from exc

        try:
            origin_file = self.file_service.get_file(entity.origin_file_key)
        except Exception as exc:
            self.logger.error(f'Failed to get transcription entity origin file: {exc}')
            raise RuntimeError('Failed to get transcription entity origin file') from exc

        return origin_file

    def get_transcription_filepath(self, id: int) -> FileEntity:
        try:
            entity = self.transcription_repo.get_by_id(id)
        except Exception as exc:
            self.logger.error(f'Failed to get transcription entity for getting transcription filepath: {exc}')
            raise RuntimeError('Failed to get transcription entity for getting transcription filepath') from exc

        try:
            transcription_file = self.file_service.get_file(entity.transcription_file_key)
        except Exception as exc:
            self.logger.error(f'Failed to get transcription entity transcription file: {exc}')
            raise RuntimeError('Failed to get transcription entity transcription file') from exc

        return transcription_file

