from dataclasses import dataclass
from typing import Any, IO

from src.module.entity.transcription_entity import TranscriptionType


@dataclass
class TranscriptionDto:
    model_settings:     dict[str, Any]
    filename:           str
    transcription_type: TranscriptionType
    file_stream:        IO
