from src.module.database.postgres.base_model import BaseSqliteModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import func
from datetime import datetime
from enum import Enum


class TranscriptionType(Enum):
    TextToSpeech = 'text_to_speech'
    SpeechToText = 'speech_to_text'


class TranscriptionEntity(BaseSqliteModel):
    __tablename__ = 'transcriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[TranscriptionType] = mapped_column(
        SqlEnum(TranscriptionType),
        nullable=False
    )
    file_path: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"TranscriptionEntity(id={self.id}, name={self.name}, type={self.type}, file_path={self.file_path})"
