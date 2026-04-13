from datetime import datetime
from pathlib import Path
from enum import Enum

from pydantic import BaseModel, Field


class TranscriptionType(Enum):
    TEXT_TO_SPEECH = 'TEXT_TO_SPEECH'
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"


class TranscriptionEntity(BaseModel):
    id: int = Field(default=None, init=False)
    transcription_type: TranscriptionType
    transcription_name: str
    transcription_filepath: Path
    origin_name: str
    origin_filepath: Path
    created_at: datetime = Field(default_factory=datetime.now)
