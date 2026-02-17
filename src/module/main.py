import src.module.logger.std_logging.logger as std_logger
from src.module.config.model import Config
from src.module.database.postgres.db import PostgresDB
from src.module.repository.transcription.repository_impl import TranscriptionRepositoryImpl
from src.module.entity.transcription_entity import TranscriptionType
from src.module.service.transcription.service_impl import TranscriptionServiceImpl

if __name__ == '__main__':
    config = Config.load()
    stg_log = std_logger.StdLogger(config.logging.std_logger)

    pg_db_name = config.perovskite_pg_dev.db_name.get_secret_value()
    pg_user = config.perovskite_pg_dev.user.get_secret_value()
    pg_password = config.perovskite_pg_dev.password.get_secret_value()
    pg_host = config.perovskite_pg_dev.host.get_secret_value()
    pg_port = config.perovskite_pg_dev.port

    pg_db = PostgresDB(f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db_name}")
    pg_db.create_tables()

    transcription_repo = TranscriptionRepositoryImpl(pg_db)
    transcription_service = TranscriptionServiceImpl(transcription_repo, stg_log)

    transcription_service.create('trans.mp3', TranscriptionType.TextToSpeech, 'sdgfg')

