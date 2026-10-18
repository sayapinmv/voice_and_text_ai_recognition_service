from abc import ABC, abstractmethod
from uuid import UUID

from src.module.entities.file import FileEntity

class FileRepository(ABC):

    @abstractmethod
    def get_by_file_key(self, file_key: UUID) -> FileEntity: pass

    @abstractmethod
    def get_by_file_keys(self, *file_keys: UUID) -> list[FileEntity]: pass

    @abstractmethod
    def create(self, entity: FileEntity) -> FileEntity: pass

    @abstractmethod
    def update(self, entity: FileEntity) -> FileEntity: pass

    @abstractmethod
    def remove_by_file_key(self, file_key: UUID): pass

    @abstractmethod
    def remove_by_file_keys(self, *file_keys: UUID): pass
