from src.module.logger.logger import Logger
from src.module.entity.transcription_entity import TranscriptionType, TranscriptionEntity
from src.module.repository.transcription.repository import TranscriptionRepository
from src.module.service.transcription.service import TranscriptionService
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import os


@dataclass
class TranscriptionDto:
    id: int
    name: str
    file_bytes: str


class AudioFileExtension(Enum):
    WAW = 'waw'
    MP3 = 'mp3'
    MP4 = 'mp4'
    MOV = 'MOV'


class TextFileExtension(Enum):
    TXT = 'txt'
    SRT = 'srt'


ALLOWED_EXTENSIONS = {
    TranscriptionType.TextToSpeech: ', '.join(ext.value for ext in AudioFileExtension),
    TranscriptionType.SpeechToText: ', '.join(ext.value for ext in TextFileExtension)
}


class TranscriptionServiceImpl(TranscriptionService):

    def __init__(self, repository: TranscriptionRepository, logger: Logger):
        self._repository = repository
        self._logger = logger

    def get(self, id: int):
        try:
            entity = self._repository.get_by_id(id)
        except Exception:
            self._logger.error(f"Failed getting message by id {id}")
            raise RuntimeError(f"Failed getting message by id {id}")

        with open(entity.file_path, mode='r', encoding='utf-8') as file:
            content = file.read()

        self._logger.info(f"Transcription by id {id} successfully got.")
        return TranscriptionDto(entity.id, entity.name, content)

    def create(self, file_name: str, transcription_type: TranscriptionType, file_bytes: str):
        extension = file_name.rsplit('.')[-1]

        if extension in ALLOWED_EXTENSIONS[transcription_type]:
            if transcription_type is TranscriptionType.TextToSpeech:
                # GET TRANSCRIPTION
                pass
            elif transcription_type is TranscriptionType.SpeechToText:
                # GET TRANSCRIPTION
                pass
        else:
            allowed_extensions = ALLOWED_EXTENSIONS[transcription_type]
            log_msg = f"Invalid file extension {extension}. Should be one of them: {allowed_extensions}"
            self._logger.error(log_msg)
            raise ValueError(log_msg)

        self._logger.debug("Transcription file successfully created.")

        try:
            existing_entity = self._repository.get_by_name_and_type(os.path.basename(file_name), transcription_type)

            if existing_entity is None:
                self._repository.create(TranscriptionEntity(file_path=f"./blablalbla/{file_name}", type=transcription_type, name=os.path.basename(file_name)))
            else:
                existing_entity.modified_at = datetime.now()
                self._repository.update(existing_entity)

        except Exception:
            log_msg = f"Failed creating transcription record by name {file_name}"
            self._logger.error(log_msg)
            raise RuntimeError(log_msg)

        self._logger.info("Transcription successfully created")

    def remove(self, id: int):
        entity = self._repository.get_by_id(id)

        if os.path.exists(entity.file_path):
            os.remove(entity.file_path)
            self._logger.debug(f"Transcription's file by id {id} successfully deleted.")
        else:
            self._logger.warning(f'File for transcription by id {id} already deleted.')

        try:
            self._repository.remove_by_id(id)
        except Exception:
            log_msg = f"Failed removing transcription record by id {id}"
            self._logger.error(log_msg)
            raise RuntimeError(log_msg)
