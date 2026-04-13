from abc import ABC, abstractmethod

from src.module.entity.transcription_entity import TranscriptionEntity, TranscriptionType


class TranscriptionRepository(ABC):

    @abstractmethod
    def get_by_id(self, id: int) -> TranscriptionEntity: pass

    @abstractmethod
    def get_by_name_and_type(self, name: str, type: TranscriptionType): pass

    @abstractmethod
    def create(self, entity: TranscriptionEntity) -> TranscriptionEntity: pass

    @abstractmethod
    def update(self, entity: TranscriptionEntity) -> TranscriptionEntity: pass

    @abstractmethod
    def remove_by_id(self, id: int): pass
