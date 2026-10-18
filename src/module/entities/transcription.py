from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class TranscriptionType(Enum):
    TEXT_TO_SPEECH = 'TEXT_TO_SPEECH'
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"


class TranscriptionEntity(BaseModel):
    id: int = Field(default=None)
    type: TranscriptionType
    name: str
    transcription_file_key: UUID
    origin_file_key: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
