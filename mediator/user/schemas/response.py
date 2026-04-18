# mediator/user/response.py

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from mediator.user.model import AuthProvider, UserStatus


# ---------- Base / shared ----------

class UserBaseResponse(BaseModel):
    """Fields safe to return in any context."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str | None
    avatar_url: str | None


# ---------- Public-facing (minimal) ----------

class UserPublicResponse(UserBaseResponse):
    """What OTHER users would see about this user (if you add sharing later)."""
    # Intentionally tiny. No email, no timestamps, no status.
    pass


# ---------- Self-facing (full profile) ----------

class UserResponse(UserBaseResponse):
    """Returned to the user themselves — their full profile."""
    email: EmailStr | None
    username: str | None
    timezone: str

    status: UserStatus
    is_anonymous: bool
    is_active: bool

    last_active_at: datetime | None


# ---------- Auth responses ----------

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int                     # seconds


class AuthResponse(BaseModel):
    """Returned after signup/login — user + tokens together."""
    user: UserResponse
    tokens: TokenResponse
    session_id: uuid.UUID


class AnonymousAuthResponse(BaseModel):
    """Day 1 anonymous flow — no tokens, just a session id."""
    user: UserResponse
    session_id: str                     # stored in an HttpOnly cookie


# ---------- Stats (for a "profile" screen in the app) ----------

class UserStatsResponse(BaseModel):
    """Ghost Mode-specific stats — lovely for a profile page."""
    model_config = ConfigDict(from_attributes=True)

    total_uploads: int
    total_personas: int                 # how many past-selves they've built
    total_sessions: int                 # how many conversations they've had
    oldest_persona_age_range: str | None   # e.g. "14-16"
    most_recent_session_at: datetime | None
    total_messages_exchanged: int


class UserProfileResponse(BaseModel):
    """One endpoint to power the entire profile screen."""
    user: UserResponse
    stats: UserStatsResponse


# ---------- Lists / admin ----------

class UserListItemResponse(UserBaseResponse):
    """Row shape for admin user lists — compact."""
    email: EmailStr | None
    status: UserStatus
    created_at: datetime
    last_active_at: datetime | None


class UserListResponse(BaseModel):
    items: list[UserListItemResponse]
    total: int
    page: int
    page_size: int


# ---------- Simple acknowledgements ----------

class MessageResponse(BaseModel):
    """Generic success ack — 'Verification email sent', etc."""
    message: str


class DeletionScheduledResponse(BaseModel):
    """Soft-delete ack — tell the user when it'll be permanent."""
    message: str = "Your account has been scheduled for deletion."
    scheduled_permanent_deletion_at: datetime
    recovery_until: datetime