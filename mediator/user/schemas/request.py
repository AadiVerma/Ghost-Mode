# mediator/user/request.py

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator

from mediator.user.model import AuthProvider


# ---------- Signup / Create ----------


class UserSignupRequest(BaseModel):
    """Email + password signup."""

    email: EmailStr
    display_name: str | None = Field(default=None, max_length=120)
    timezone: str = Field(default="UTC", max_length=64)

    has_accepted_terms: bool
    has_accepted_emotional_disclaimer: bool

    @field_validator("has_accepted_terms", "has_accepted_emotional_disclaimer")
    @classmethod
    def must_accept(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Consent is required to use Ghost Mode.")
        return v


class UserOAuthSignupRequest(BaseModel):
    """Google / Apple signup — token verified separately."""

    provider: AuthProvider
    oauth_token: str
    timezone: str = Field(default="UTC", max_length=64)

    has_accepted_terms: bool
    has_accepted_emotional_disclaimer: bool


class AnonymousUserCreateRequest(BaseModel):
    """Day 1 flow — no auth, just a session cookie."""

    timezone: str = Field(default="UTC", max_length=64)
    has_accepted_emotional_disclaimer: bool = True


# ---------- OTP ----------


class RequestOTPRequest(BaseModel):
    """Request OTP for login/signup."""

    email: EmailStr


class VerifyOTPRequest(BaseModel):
    """Verify OTP and login/signup."""

    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6, pattern="^[0-9]{6}$")


# ---------- Update ----------


class UserUpdateRequest(BaseModel):
    """Fields a user is allowed to change about themselves."""

    display_name: str | None = Field(default=None, max_length=120)
    avatar_url: str | None = Field(default=None, max_length=512)
    timezone: str | None = Field(default=None, max_length=64)


class UserPasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def not_same_as_current(cls, v: str, info) -> str:
        if v == info.data.get("current_password"):
            raise ValueError("New password must differ from current password.")
        return v


class UpgradeAnonymousRequest(BaseModel):
    """Convert an anonymous user into a real account."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


# ---------- Account actions ----------


class UserDeleteRequest(BaseModel):
    """Soft delete — requires explicit confirmation on an emotional product."""

    password: str | None = None  # null for anonymous / OAuth users
    confirmation_phrase: str = Field(
        description='Must match exactly: "delete my ghost"',
    )

    @field_validator("confirmation_phrase")
    @classmethod
    def must_match(cls, v: str) -> str:
        if v.strip().lower() != "delete my ghost":
            raise ValueError('Confirmation phrase must be "delete my ghost".')
        return v


class EmailVerificationRequest(BaseModel):
    token: str


class LogoutRequest(BaseModel):
    """Logout request with session ID."""

    id: str
