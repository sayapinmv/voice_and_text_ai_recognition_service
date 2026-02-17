from src.module.entity.transcription_entity import TranscriptionType
from abc import ABC, abstractmethod


class TranscriptionService(ABC):

    @abstractmethod
    def get(self, id: int): pass

    @abstractmethod
    def create(self, file_name: str, transcription_type: TranscriptionType, file_bytes: str): pass

    @abstractmethod
    def remove(self, id: int): pass
