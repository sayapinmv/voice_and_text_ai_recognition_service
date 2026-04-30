from typing import Any

from pydantic import BaseModel, Field

from src.module.entity.transcription_entity import (TranscriptionType)


class GetTranscriptionResponse(BaseModel):
    id: int = Field(ge=0)
    transcription_type: TranscriptionType
    transcription_name: str
    origin_name: str


class CreateRecognitionRequest(BaseModel):
    transcription_type: str
    transcription_ai_settings: dict[str, Any]

