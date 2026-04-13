from abc import ABC, abstractmethod

from src.module.entity.transcription_entity import TranscriptionType, TranscriptionEntity
from src.module.repository.transcription.repository import TranscriptionRepository
from src.module.service.recognition.service import RecognitionService
from src.module.service.transcription.model import TranscriptionDto
from src.module.logger.logger import Logger


class TranscriptionService(ABC):

    def __init__(self,
                 speech_to_text_service: RecognitionService,
                 text_to_speech_service: RecognitionService,
                 transcription_repo: TranscriptionRepository,
                 logger: Logger):

        self.speech_to_text_service = speech_to_text_service
        self.text_to_speech_service = text_to_speech_service
        self.transcription_repo = transcription_repo
        self.logger = logger

    @abstractmethod
    def get(self, id: int) -> TranscriptionEntity: pass

    @abstractmethod
    def create(self, transcription_dto: TranscriptionDto) -> TranscriptionEntity: pass

    @abstractmethod
    def remove(self, id: int): pass
