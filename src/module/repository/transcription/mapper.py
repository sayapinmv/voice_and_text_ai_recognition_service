from pathlib import Path

from src.module.database.orm.postgres.models.transcription_model import TranscriptionModel
from src.module.entity.transcription_entity import TranscriptionEntity


def to_transcription_model(entity: TranscriptionEntity) -> TranscriptionModel:
    return TranscriptionModel(
        id=entity.id,
        transcription_type=entity.transcription_type,
        transcription_name=entity.transcription_name,
        transcription_filepath=str(entity.transcription_filepath),
        origin_name=entity.origin_name,
        origin_filepath=str(entity.origin_filepath),
        created_at=entity.created_at,
    )


def to_transcription_entity(model: TranscriptionModel) -> TranscriptionEntity:
    return TranscriptionEntity(
        id=model.id,
        transcription_type=model.transcription_type,
        transcription_name=model.transcription_name,
        transcription_filepath=Path(model.transcription_filepath),
        origin_name=model.origin_name,
        origin_filepath=Path(model.origin_filepath),
        created_at=model.created_at,
    )
