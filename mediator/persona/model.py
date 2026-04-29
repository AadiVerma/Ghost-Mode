from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB

from config.database.base import Base

class PersonaStatus(str, Enum):
    EXTRACTING = "extracting"
    READY = "ready"
    FAILED = "failed"

class Persona(Base):
    """
    An extracted "past self" at a specific age range.
    """
    __tablename__ = "personas"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    age_range: Mapped[str] = mapped_column(String(32), nullable=False)

    voice_signature: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    themes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    beliefs: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    fears: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    relationships: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    sample_messages: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    status: Mapped[PersonaStatus] = mapped_column(
        SQLEnum(PersonaStatus),
        default=PersonaStatus.EXTRACTING,
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        return f"<Persona {self.id} age={self.age_range} status={self.status}>"
