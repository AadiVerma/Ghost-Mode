from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from config.database.base import Base

class Message(Base):
    """
    A single line of parsed message from an Upload.
    """
    __tablename__ = "messages"

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    sender: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    is_media: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Message {self.id} sender={self.sender} timestamp={self.timestamp}>"
