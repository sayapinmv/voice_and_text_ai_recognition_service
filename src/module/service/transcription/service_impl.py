import os

from src.module.logger.logger import Logger
from src.module.entity.transcription_entity import TranscriptionType, TranscriptionEntity
from src.module.repository.transcription.repository import TranscriptionRepository
from src.module.service.transcription.service import TranscriptionService
from src.module.service.transcription.model import TranscriptionDto
from src.module.service.recognition.service import RecognitionService


class TranscriptionServiceImpl(TranscriptionService):

    def __init__(self,
                 speech_to_text_service: RecognitionService,
                 text_to_speech_service: RecognitionService,
                 transcription_repo: TranscriptionRepository,
                 logger: Logger):

        super().__init__(speech_to_text_service, text_to_speech_service, transcription_repo, logger)

    def get(self, id: int):
        try:
            entity = self.transcription_repo.get_by_id(id)
        except Exception as exc:
            self.logger.error(f"Failed getting transcription by id {id}. err: {exc}")
            raise RuntimeError(f"Failed getting transcription by id {id}. err: {exc}")

        return entity

    def create(self, transcription_dto: TranscriptionDto) -> TranscriptionEntity:
        self.logger.info("Start creating transcription")

        if transcription_dto.transcription_type is TranscriptionType.TEXT_TO_SPEECH:
            try:
                entity = self.text_to_speech_service.create_transcription(
                    transcription_dto.filename,
                    transcription_dto.file_stream,
                    transcription_dto.model_settings
                )

                print(entity)
            except Exception as exc:
                raise exc
            
        elif transcription_dto.transcription_type is TranscriptionType.SPEECH_TO_TEXT:
            try:
                entity = self.speech_to_text_service.create_transcription(
                    transcription_dto.filename,
                    transcription_dto.file_stream,
                    transcription_dto.model_settings
                )

                print(entity)
            except Exception as exc:
                raise exc

        self.logger.debug("Transcription file successfully created.")

        try:
            new_entity = self.transcription_repo.create(entity)
        except Exception:
            log_msg = f"Failed creating transcription record by name {transcription_dto.filename}"
            self.logger.error(log_msg)
            raise RuntimeError(log_msg)

        self.logger.info("Transcription successfully created")
        return new_entity

    def remove(self, id: int):
        entity = self.transcription_repo.get_by_id(id)

        if os.path.exists(entity.transcription_filepath):
            os.remove(entity.transcription_filepath)
            self.logger.debug(f"Transcription file by id {id} successfully deleted.")
        else:
            self.logger.warning(f'Transcription file for entity by id {id} already deleted.')

        if os.path.exists(entity.origin_filepath):
            os.remove(entity.origin_filepath)
            self.logger.debug(f"Origin file by id {id} successfully deleted.")
        else:
            self.logger.warning(f'Origin file for entity by id {id} already deleted.')

        try:
            self.transcription_repo.remove_by_id(id)
        except Exception:
            log_msg = f"Failed removing transcription record by id {id}"
            self.logger.error(log_msg)
            raise RuntimeError(log_msg)
