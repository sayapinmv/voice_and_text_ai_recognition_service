import uuid
from enum import Enum
from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone

from pydantic import BaseModel, Field

class FileType(Enum):
    Media = "media"
    Text = "text"

class FileEntity(BaseModel):
    file_key: UUID = Field(default_factory=uuid.uuid4)
    filename: str
    filepath: Path
    type: FileType
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))