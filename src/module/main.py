from fastapi import FastAPI
import uvicorn

import src.module.logger.std_logging.logger as std_logger
from src.module.config.provider_factory import ConfigProviderFactoryImpl
from src.module.database.orm.postgres.db import PostgresDB
from src.module.repository.transcription.repository_impl import TranscriptionRepositoryImpl
from src.module.config.builder import ConfigBuilderImpl
from src.module.service.transcription.service_impl import TranscriptionServiceImpl
from src.module.controller.transcription_controller import TranscriptionsController
from src.module.service.file_storage.disk_storage.disk_storage_service_impl import DiskFileStorageServiceImpl
from src.module.service.recognition.speech_to_text.whisper_service_impl import WhisperServiceImpl
from src.module.service.recognition.text_to_speech.qwen_tts_service_impl import QwenTTSServiceImpl

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine, select


if __name__ == '__main__':
    env_provider = ConfigProviderFactoryImpl.create('env', './.env')
    yaml_provider = ConfigProviderFactoryImpl.create('yml', './config.yaml')
    config = ConfigBuilderImpl().add_provider(env_provider).add_provider(yaml_provider).build()

    std_log = std_logger.StdLogger(config.logging.std_logger)

    pg_db = PostgresDB(config.pg_perovskite_dev.connection_string)
    pg_db.create_tables()

    stt_origins_storage = DiskFileStorageServiceImpl(config.ai_models.speech_to_text.origins_dirpath, 8184)
    stt_transcriptions_storage = DiskFileStorageServiceImpl(config.ai_models.speech_to_text.transcriptions_dirpath, 8184)

    transcription_repo = TranscriptionRepositoryImpl(pg_db)
    whisper = WhisperServiceImpl(
        config.ai_models.speech_to_text.model_settings,
        stt_origins_storage,
        stt_transcriptions_storage,
        std_log
    )

    qwen_tts_service = QwenTTSServiceImpl(
        {},
        stt_transcriptions_storage,
        stt_origins_storage,
        std_log
    )

    transcription_service = TranscriptionServiceImpl(whisper, qwen_tts_service, transcription_repo, std_log)

    std_log.info("sfdsf")

    transcriptions_controller = TranscriptionsController(std_log, transcription_service)

    app = FastAPI()

    app.include_router(transcriptions_controller.router)

    uvicorn.run(app, host=config.server.host, port=config.server.port)

    engine = create_engine('connection_url')
    session = sessionmaker()
    with session() as session:
        scalar = select().where()



