from datetime import datetime, timezone
import uuid
from pathlib import Path

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from src.module.database.orm.postgres.base_model import BasePostgresModel
from src.module.entities.file import FileType


class FileModel(BasePostgresModel):
    __tablename__ = 'file'

    file_key: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(nullable=False)
    filepath: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[FileType] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc))