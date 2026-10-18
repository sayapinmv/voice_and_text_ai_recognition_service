from sqlalchemy import select

from src.module.database.orm.postgres.db import PostgresDB
from src.module.database.orm.postgres.transcription.model import TranscriptionModel
from src.module.entities.transcription import TranscriptionType, TranscriptionEntity
from src.module.repository.transcription import TranscriptionRepository


def to_transcription_model(entity: TranscriptionEntity) -> TranscriptionModel:
    return TranscriptionModel(
        id=entity.id,
        type=entity.type,
        name=entity.name,
        transcription_file_key=entity.transcription_file_key,
        origin_file_key=entity.origin_file_key,
        created_at=entity.created_at,
    )


def to_transcription_entity(model: TranscriptionModel) -> TranscriptionEntity:
    return TranscriptionEntity(
        id=model.id,
        type=model.type,
        name=model.name,
        transcription_file_key=model.transcription_file_key,
        origin_file_key=model.origin_file_key,
        created_at=model.created_at,
    )

class TranscriptionRepositoryImpl(TranscriptionRepository):

    def __init__(self, db: PostgresDB):
        self._db = db

    def get_by_id(self, id: int) -> TranscriptionEntity:
        with self._db.get_session() as session:
            statement = select(TranscriptionModel).where(TranscriptionModel.id == id)
            model = session.scalars(statement).first()
            return to_transcription_entity(model)

    def get_by_name_and_type(self, name: str, type: TranscriptionType):
        with self._db.get_session() as session:
            statement = select(TranscriptionModel).where(
                TranscriptionModel.name == name,
                TranscriptionModel.type == type.value
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