from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from src.module.database.orm.postgres.db import PostgresDB
from src.module.database.orm.postgres.file.model import FileModel
from src.module.entities.file import FileEntity
from src.module.repository.file import FileRepository

def to_file_model(entity: FileEntity) -> FileModel:
    return FileModel(
        file_key=entity.file_key,
        filename=entity.filename,
        filepath=str(entity.filepath),
        type=entity.type,
        created_at=entity.created_at,
    )

def to_file_entity(entity: FileModel) -> FileEntity:
    return FileEntity(
        file_key=entity.file_key,
        filename=entity.filename,
        filepath=Path(entity.filepath),
        type=entity.type,
        created_at=entity.created_at,
    )


class FileRepositoryImpl(FileRepository):

    def __init__(self, db: PostgresDB):
        self._db = db

    def get_by_file_key(self, file_key: UUID) -> FileEntity:
        with self._db.get_session() as session:
            statement = select(FileModel).where(FileModel.file_key == file_key)
            model = session.scalars(statement).first()

            if model is None:
                raise ValueError(f"entity with file_key {file_key} not found")
            return to_file_entity(model)

    def get_by_file_keys(self, *file_keys: UUID) -> list[FileEntity]:
        with self._db.get_session() as session:
            statement = select(FileModel).where(FileModel.file_key.in_(file_keys))
            models = session.scalars(statement).all()

            if models is None:
                raise ValueError(f"Entities by file_keys {file_keys} not found")

            result = []
            for model in models:
                result.append(to_file_model(model))

            return result

    def create(self, entity: FileEntity) -> FileEntity:
        model = to_file_model(entity)
        with self._db.get_session() as session:
            try:
                session.add(model)
                session.commit()
                return to_file_entity(model)
            except Exception as exc:
                session.rollback()
                raise exc
            finally:
                session.close()

    def update(self, entity: FileEntity) -> FileEntity:
        model = to_file_model(entity)
        with self._db.get_session() as session:
            try:
                session.merge(model)
                session.commit()
                return to_file_entity(model)
            except Exception as exc:
                session.rollback()
                raise exc
            finally:
                session.close()

    def remove_by_file_key(self, file_key: UUID):
        with self._db.get_session() as session:
            try:
                result = session.query(FileModel).filter(FileModel.file_key == file_key).delete()
                session.commit()

                if result == 0:
                    raise ValueError(f"Entity with id {file_key} not found")

            except Exception as exc:
                session.rollback()
                raise exc
            finally:
                session.close()

    def remove_by_file_keys(self, *file_keys: UUID):
        with self._db.get_session() as session:
            try:
                result = session.query(FileModel).filter(FileModel.file_key.in_(file_keys)).delete(synchronize_session=False)
                session.commit()

                if result == 0:
                    raise ValueError(f"Entity with file_keys {file_keys} not found")

            except Exception as exc:
                session.rollback()
                raise exc
            finally:
                session.close()
