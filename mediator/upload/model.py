from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from config.database.base import Base

class UploadSource(str, Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"

class UploadStatus(str, Enum):
    QUEUED = "queued"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"

class Upload(Base):
    """
    A raw chat export file uploaded by the user.
    """
    __tablename__ = "uploads"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    source: Mapped[UploadSource] = mapped_column(
        SQLEnum(UploadSource),
        default=UploadSource.WHATSAPP,
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(String(512), nullable=False)

    status: Mapped[UploadStatus] = mapped_column(
        SQLEnum(UploadStatus),
        default=UploadStatus.QUEUED,
        nullable=False,
        index=True
    )

    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Upload {self.id} (source={self.source}, status={self.status})>"
