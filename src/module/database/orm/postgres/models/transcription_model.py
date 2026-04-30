from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import func

from src.module.database.orm.postgres.models.base_model import BasePostgresModel
from src.module.entity.transcription_entity import TranscriptionType


class TranscriptionModel(BasePostgresModel):
    __tablename__ = 'transcriptions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transcription_type: Mapped[TranscriptionType] = mapped_column(
        SqlEnum(TranscriptionType),
        nullable=False
    )
    transcription_name: Mapped[str] = mapped_column(nullable=False)
    transcription_filepath: Mapped[str] = mapped_column(nullable=False)
    origin_name: Mapped[str] = mapped_column(nullable=False)
    origin_filepath: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )
