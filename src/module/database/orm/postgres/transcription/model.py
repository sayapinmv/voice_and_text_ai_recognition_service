from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SqlEnum, Uuid

from src.module.database.orm.postgres.base_model import BasePostgresModel
from src.module.entities.transcription import TranscriptionType


class TranscriptionModel(BasePostgresModel):
    __tablename__ = 'transcriptions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[TranscriptionType] = mapped_column(SqlEnum(TranscriptionType), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    transcription_file_key: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    origin_file_key: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))
