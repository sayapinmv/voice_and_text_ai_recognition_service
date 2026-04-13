from sqlalchemy import select

from src.module.repository.transcription.repository import TranscriptionRepository, TranscriptionType
from src.module.entity.transcription_entity import TranscriptionEntity
from src.module.database.orm.postgres.db import PostgresDB
from src.module.logger.logger import Logger
from src.module.database.orm.postgres.models.transcription_model import TranscriptionModel
from src.module.repository.transcription.mapper import to_transcription_model, to_transcription_entity


class TranscriptionRepositoryImpl(TranscriptionRepository):

    def __init__(self, db: PostgresDB, logger: Logger = None):
        self._db = db
        self._logger = logger

    def get_by_id(self, id: int) -> TranscriptionEntity:
        with self._db.get_session() as session:
            statement = select(TranscriptionModel).where(TranscriptionModel.id == id)
            model = session.scalars(statement).first()
            return to_transcription_entity(model)

    def get_by_name_and_type(self, transcription_name: str, transcription_type: TranscriptionType):
        with self._db.get_session() as session:
            statement = select(TranscriptionModel).where(
                TranscriptionModel.transcription_name == transcription_name,
                TranscriptionModel.transcription_type == transcription_type.value
            )

            model = session.scalars(statement).first()
            if model is None:
                return model
            return to_transcription_entity(model)

    def create(self, entity: TranscriptionEntity) -> TranscriptionEntity:
        model = to_transcription_model(entity)
        with self._db.get_session() as session:
            try:
                session.add(model)
                session.commit()
                return to_transcription_entity(model)
            except Exception as exc:
                session.rollback()
                raise exc
            finally:
                session.close()

    def update(self, entity: TranscriptionEntity) -> TranscriptionEntity:
        model = to_transcription_model(entity)
        with self._db.get_session() as session:
            try:
                session.merge(model)
                session.commit()
                return to_transcription_entity(model)
            except Exception as exc:
                session.rollback()
                raise exc
            finally:
                session.close()

    def remove_by_id(self, id: int):
        with self._db.get_session() as session:
            try:
                result = session.query(TranscriptionModel).filter(TranscriptionModel.id == id).delete()
                session.commit()

                if result == 0:
                    raise ValueError(f"Entity with id {id} not found")

            except Exception as exc:
                session.rollback()
                raise exc
            finally:
                session.close()
