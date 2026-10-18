from pathlib import Path

from src.module.entities.file import FileType
from src.module.logger.logger import Logger
from src.module.entities.transcription import TranscriptionType, TranscriptionEntity
from src.module.repository.transcription import TranscriptionRepository

from src.module.service.file_storage.service import FileStorageService, FileDto
from src.module.service.transcription.service import TranscriptionService, TranscriptionDto
from src.module.service.recognition.service import RecognitionService, RecognitionDto

FILE_TYPE_BY_TRANSCRIPTION_TYPE = {
    TranscriptionType.SPEECH_TO_TEXT : FileType.Media,
    TranscriptionType.TEXT_TO_SPEECH: FileType.Text,
}


class TranscriptionServiceImpl(TranscriptionService):

    def __init__(self,
                 recognition_services: dict[TranscriptionType, RecognitionService],
                 transcription_repo: TranscriptionRepository,
                 file_service: FileStorageService,
                 logger: Logger):

        super().__init__(recognition_services, transcription_repo, file_service, logger)

    def get(self, id: int):
        try:
            entity = self.transcription_repo.get_by_id(id)
        except Exception as exc:
            self.logger.error(f"Failed getting transcription by id {id}. err: {exc}")
            raise RuntimeError(f"Failed getting transcription by id {id}. err: {exc}")

        return entity

    def create(self, transcription_dto: TranscriptionDto) -> TranscriptionEntity:
        self.logger.info("Start creating transcription")

        if transcription_dto.type not in self.recognition_services:
            raise ValueError('Invalid transcription type')

        original_file = None
        transcription_file = None

        try:
            origin_file_data = transcription_dto.file.read()
            transcription_dto.file.seek(0)

            origin_file = FileDto(
                type=FILE_TYPE_BY_TRANSCRIPTION_TYPE[transcription_dto.type],
                filepath=Path("inputs") / Path(transcription_dto.type.value.lower()) / Path(transcription_dto.filename).name,
                file_data=origin_file_data,
            )
            original_file = self.file_service.create_file(origin_file)

            recognition_service = self.recognition_services[transcription_dto.type]
            recognition_dto = RecognitionDto(
                filename=transcription_dto.filename,
                file=transcription_dto.file,
                model_settings=transcription_dto.model_settings,
            )

            transcription_file = recognition_service.create_transcription(recognition_dto)
            self.logger.debug("Transcription file successfully created.")

            entity = TranscriptionEntity(
                type=transcription_dto.type,
                name=Path(transcription_dto.filename).stem,
                transcription_file_key=transcription_file.file_key,
                origin_file_key=original_file.file_key
            )

            entity = self.transcription_repo.create(entity)

        except Exception as exc:
            for file_entity in (transcription_file, original_file):
                if file_entity is not None:
                    try:
                        self.file_service.remove(file_entity.file_key)
                    except Exception as cleanup_exc:
                        self.logger.error(
                            f"Failed to clean up file "
                            f"{file_entity.file_key}: {cleanup_exc}"
                        )

            self.logger.error(f"Failed creating transcription: {exc}")
            raise RuntimeError("Failed to create transcription") from exc

        self.logger.info("Transcription successfully created")
        return entity

    def remove(self, id: int):
        try:
            entity = self.transcription_repo.get_by_id(id)
        except Exception as exc:
            self.logger.error(f'Failed to get transcription entity for removing: {exc}')
            raise RuntimeError('Failed to get transcription for removing') from exc

        try:
            self.file_service.remove_by_keys(entity.transcription_file_key, entity.origin_file_key)
        except Exception as exc:
            self.logger.error(f'Failed removing transcription file entities: {exc}')
            raise RuntimeError('Failed removing transcription file entities') from exc

        try:
            self.transcription_repo.remove_by_id(id)
        except Exception:
            log_msg = f"Failed removing transcription record by id {id}"
            self.logger.error(log_msg)
            raise RuntimeError(log_msg)
