import os
from pathlib import Path
from typing import Any
from uuid import UUID
import numpy as np
import soundfile as sf

from src.module.entities.file import FileEntity
from src.module.repository.file import FileRepository
from src.module.service.file_storage.service import FileDto, EXTENSIONS_BY_FILE_TYPE, is_valid_file_extension, \
    get_allowed_extensions, get_unique_filepath, FileStorageService, FileType

DEFAULT_SAMPLE_RATE = 16000

def _write_audio(filepath: Path, file_dto: FileDto) -> None:
    if file_dto.meta is None or file_dto.meta['sample_rate'] is None:
        with filepath.open("xb") as destination:
            destination.write(file_dto.file_data)
            return

    audio = np.frombuffer(file_dto.file_data, dtype=np.float32)
    sf.write(
        str(filepath),
        audio,
        file_dto.meta['sample_rate'],
        subtype="FLOAT",
        format="WAV",
    )

class FileStorageServiceImpl(FileStorageService):
    def __init__(self, file_repo: FileRepository) -> None:
        super().__init__(file_repo)

    def get_file(self, file_key: UUID) -> FileEntity:
        return self._file_repo.get_by_file_key(file_key)

    def get_files_by_keys(self, *file_keys: UUID) -> list[FileEntity]:
        return self._file_repo.get_by_file_keys(*file_keys)

    def create_file(self, file_dto: FileDto) -> FileEntity:
        if file_dto is None:
            raise ValueError("file_dto is None")

        if file_dto.file_data is None:
            raise ValueError("file_data is None")

        if file_dto.type not in EXTENSIONS_BY_FILE_TYPE:
            raise ValueError(f"Unsupported file type: {file_dto.type}")

        if not is_valid_file_extension(file_dto.filepath, file_dto.type):
            allowed = ", ".join(get_allowed_extensions(file_dto.type))
            raise ValueError(
                f"Invalid file extension for {file_dto.filepath}. "
                f"Allowed extensions: {allowed}"
            )

        requested_filepath = file_dto.filepath
        requested_filepath.parent.mkdir(parents=True, exist_ok=True)

        while True:
            filepath = get_unique_filepath(requested_filepath)

            try:
                match file_dto.type:
                    case FileType.Media:
                        _write_audio(filepath, file_dto)
                    case FileType.Text:
                        with filepath.open("xb") as destination:
                            destination.write(file_dto.file_data)
                    case _:
                        raise ValueError('Invalid')
                break
            except FileExistsError:
                continue
            except Exception:
                filepath.unlink(missing_ok=True)
                raise

        file_entity = FileEntity(
            type=file_dto.type,
            filename=filepath.name,
            filepath=filepath,
        )

        try:
            file_entity = self._file_repo.create(file_entity)
        except Exception:
            filepath.unlink(missing_ok=True)
            raise

        return file_entity

    def remove(self, file_key):
        try:
            file_entity = self.get_file(file_key)
            self._file_repo.remove_by_file_key(file_key)

            if os.path.exists(file_entity.filepath):
                os.remove(file_entity.filepath)
            else:
                raise RuntimeError(f"File {file_entity.filepath} does not exist")
        except Exception:
            raise

    def remove_by_keys(self, *file_keys: UUID):
        try:
            file_entities = self.get_files_by_keys(*file_keys)
            self._file_repo.remove_by_file_keys(*file_keys)

            for file_entity in file_entities:
                if os.path.exists(file_entity.filepath):
                    os.remove(file_entity.filepath)
                else:
                    raise RuntimeError(f"File {file_entity.filepath} does not exist")
        except Exception:
            raise
