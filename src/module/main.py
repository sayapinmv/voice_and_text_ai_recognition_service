from fastapi import FastAPI
import uvicorn

import src.module.logger.std_logging.logger as std_logger
from src.module.config.provider_factory import ConfigProviderFactoryImpl
from src.module.database.orm.postgres.db import PostgresDB
from src.module.config.builder import ConfigBuilderImpl
from src.module.database.orm.postgres.file.repository_impl import FileRepositoryImpl
from src.module.database.orm.postgres.transcription.repository_impl import TranscriptionRepositoryImpl
from src.module.entities.transcription import TranscriptionType
from src.module.service.file_storage.service_impl import FileStorageServiceImpl
from src.module.service.recognition.text_to_speech.qwen_tts_service_impl import QwenTTSServiceImpl
from src.module.service.transcription.service_impl import TranscriptionServiceImpl
from src.module.controller.transcription import TranscriptionsController
from src.module.service.recognition.speech_to_text.whisper_service_impl import WhisperServiceImpl
from src.module.service.recognition.service import Config as RecognitionServiceConfig


if __name__ == '__main__':
    env_provider = ConfigProviderFactoryImpl.create('env', './.env')
    yaml_provider = ConfigProviderFactoryImpl.create('yml', './config.yaml')
    config = ConfigBuilderImpl().add_provider(env_provider).add_provider(yaml_provider).build()

    std_log = std_logger.StdLogger(config.logging.std_logger)

    pg_db = PostgresDB(config.pg_perovskite_dev.connection_string)
    pg_db.create_tables()

    file_repo = FileRepositoryImpl(pg_db)
    file_service = FileStorageServiceImpl(file_repo)

    transcription_repo = TranscriptionRepositoryImpl(pg_db)
    whisper = WhisperServiceImpl(
        RecognitionServiceConfig(
            model_settings=config.ai_models.speech_to_text.model_settings,
            default_transcription_settings=config.ai_models.speech_to_text.default_transcription_settings
        ),
        file_service,
        std_log
    )

    qwen_tts = QwenTTSServiceImpl(
        RecognitionServiceConfig(
            model_settings=config.ai_models.text_to_speech.model_settings,
            default_transcription_settings=config.ai_models.text_to_speech.default_transcription_settings
        ),
        file_service,
        std_log
    )

    recognition_services = {
        TranscriptionType.SPEECH_TO_TEXT: whisper,
        TranscriptionType.TEXT_TO_SPEECH: qwen_tts,
    }
    transcription_service = TranscriptionServiceImpl(recognition_services, transcription_repo, file_service, std_log)

    transcriptions_controller = TranscriptionsController(std_log, transcription_service)

    app = FastAPI()
    app.include_router(transcriptions_controller.router)
    uvicorn.run(app, host=config.server.host, port=config.server.port)

    # engine = create_engine('connection_url')
    # session = sessionmaker()
    # with session() as session:
    #     scalar = select().where()



