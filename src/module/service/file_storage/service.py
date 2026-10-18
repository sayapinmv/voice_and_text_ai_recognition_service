from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from typing import Any
from uuid import UUID
from abc import ABC, abstractmethod

from src.module.entities.file import FileEntity, FileType
from src.module.repository.file import FileRepository


class MediaFileExtension(Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    MOV = "mov"
    MP4 = "mp4"


class TextFileExtension(Enum):
    TXT = "txt"
    SRT = "srt"
    JSON = "json"
    VTT = "vtt"


EXTENSIONS_BY_FILE_TYPE = {
    FileType.Media: MediaFileExtension,
    FileType.Text: TextFileExtension,
}

@dataclass
class FileDto:
    type: FileType
    filepath: Path
    file_data: bytes
    meta: dict[str, Any] = None

def is_valid_file_extension(filepath: Path, file_type: FileType) -> bool:
    extensions = EXTENSIONS_BY_FILE_TYPE.get(file_type)
    if extensions is None:
        return False

    file_extension = filepath.suffix.lower().lstrip(".")
    return file_extension in {ext.value.lower() for ext in extensions}


def get_allowed_extensions(file_type: FileType) -> list[str]:
    extensions = EXTENSIONS_BY_FILE_TYPE.get(file_type)

    if extensions is None:
        return []

    return [f".{ext.value}" for ext in extensions]


def get_unique_filepath(filepath: Path) -> Path:
    if not filepath.exists():
        return filepath

    counter = 1
    while True:
        candidate = filepath.with_name(
            f"{filepath.stem} ({counter}){filepath.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1

class FileStorageService(ABC):
    def __init__(self, file_repo: FileRepository):
        self._file_repo = file_repo

    @abstractmethod
    def get_file(self, file_key: UUID) -> FileEntity: pass

    @abstractmethod
    def get_files_by_keys(self, *file_keys: UUID) -> list[FileEntity]: pass

    @abstractmethod
    def create_file(self, file_dto: FileDto) -> FileEntity: pass

    @abstractmethod
    def remove(self, file_key: UUID): pass

    @abstractmethod
    def remove_by_keys(self, *file_keys: UUID): pass