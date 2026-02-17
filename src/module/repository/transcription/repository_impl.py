from src.module.repository.transcription.repository import TranscriptionRepository, TranscriptionType
from src.module.entity.transcription_entity import TranscriptionEntity
from src.module.database.postgres.db import PostgresDB
from src.module.logger.logger import Logger
from sqlalchemy import select


class TranscriptionRepositoryImpl(TranscriptionRepository):

    def __init__(self, db: PostgresDB, logger: Logger = None):
        self._db = db
        self._logger = logger

    def get_by_id(self, id: int) -> TranscriptionEntity:
        with self._db.get_session() as session:
            statement = select(TranscriptionEntity).where(TranscriptionEntity.id == id)
            entity = session.scalars(statement).first()
            return entity

    def get_by_name_and_type(self, name: str, transcription_type: TranscriptionType):
        with (self._db.get_session() as session):
            statement = select(TranscriptionEntity).where(TranscriptionEntity.name == name, TranscriptionEntity.type == transcription_type.name)
            entity = session.scalars(statement).first()
            return entity

    def create(self, entity: TranscriptionEntity):
        with self._db.get_session() as session:
            try:
                session.add(entity)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()

    def update(self, entity: TranscriptionEntity):
        with self._db.get_session() as session:
            try:
                session.merge(entity)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()

    def remove_by_id(self, id: int):
        entity = self.get_by_id(id)

        with self._db.get_session() as session:
            try:
                session.delete(entity)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
