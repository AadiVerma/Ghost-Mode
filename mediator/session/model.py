from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from config.database.base import Base

class SessionStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"

class SessionRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Session(Base):
    """
    An active chat session between a User and a Persona.
    """
    __tablename__ = "sessions"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status: Mapped[SessionStatus] = mapped_column(
        SQLEnum(SessionStatus),
        default=SessionStatus.ACTIVE,
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        return f"<Session {self.id} status={self.status}>"

class SessionMessage(Base):
    """
    Individual chat messages in a session.
    """
    __tablename__ = "session_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role: Mapped[SessionRole] = mapped_column(
        SQLEnum(SessionRole),
        nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<SessionMessage {self.id} role={self.role}>"
