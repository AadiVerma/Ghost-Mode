from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum

from config.database.base import Base


class UserStatus(str, Enum):
    """Lifecycle status of a user account."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class AuthProvider(str, Enum):
    """How the user signed up."""
    EMAIL = "email"
    GOOGLE = "google"
    APPLE = "apple"
    ANONYMOUS = "anonymous"


class User(Base):
    """
    A Ghost Mode user.

    Owns uploads (chat exports), personas (extracted past selves),
    and sessions (conversations with those past selves).
    """

    __tablename__ = "users"

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=True,
    )

    display_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(
        SQLEnum(AuthProvider),
        default=AuthProvider.ANONYMOUS,
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    has_accepted_terms: Mapped[bool] = mapped_column(Boolean, default=False)
    has_accepted_emotional_disclaimer: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    consent_accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE and self.deleted_at is None

    @property
    def is_anonymous(self) -> bool:
        return self.auth_provider == AuthProvider.ANONYMOUS

    def __repr__(self) -> str:
        ident = self.email or self.username or str(self.id)
        return f"<User {ident} ({self.status.value})>"
