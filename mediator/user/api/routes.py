from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta, timezone

from mediator.user.model import User, UserOTP, UserSession
from mediator.user.schemas.response import UserPublicResponse, UserResponse, AuthResponse, TokenResponse, MessageResponse
from mediator.user.schemas.request import RequestOTPRequest, VerifyOTPRequest, LogoutRequest
from mediator.user.utils import create_access_token, create_refresh_token
from config.settings import get_settings
from config.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)

settings = get_settings()


@router.get(
    "/{user_id}",
    response_model=UserPublicResponse,
    summary="Get User by ID",
    description="Retrieve a specific User",
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> UserPublicResponse:
    """Fetch a user by their ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post(
    "/request-otp",
    response_model=MessageResponse,
    summary="Request OTP",
    description="Request OTP for signup/login",
)
async def request_otp(
    request: RequestOTPRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Request OTP for email."""
    # Find or check if user exists
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # For new users, create them as anonymous
    if not user:
        user = User(
            email=request.email,
            auth_provider="email",
            status="active",
        )
        db.add(user)
        await db.flush()

    # Generate OTP
    otp_code = UserOTP.generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    otp = UserOTP(
        user_id=user.id,
        email=request.email,
        otp_code=otp_code,
        expires_at=expires_at,
    )
    db.add(otp)
    await db.commit()

    # TODO: Send OTP via email
    # For now, return in response (remove in production)
    if settings.debug:
        return MessageResponse(message=f"OTP sent to {request.email}. Code: {otp_code}")
    return MessageResponse(message=f"OTP sent to {request.email}")


@router.post(
    "/verify-otp",
    response_model=AuthResponse,
    summary="Verify OTP and Login/Signup",
    description="Verify OTP code and create session",
)
async def verify_otp(
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Verify OTP and authenticate user."""
    # Find user by email
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or OTP",
        )

    # Find valid OTP
    stmt = select(UserOTP).where(
        (UserOTP.user_id == user.id)
        & (UserOTP.email == request.email)
        & (UserOTP.is_used == False)
    ).order_by(UserOTP.created_at.desc()).limit(1)

    result = await db.execute(stmt)
    otp = result.scalar_one_or_none()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or OTP",
        )

    if otp.is_expired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP expired",
        )

    if otp.otp_code != request.otp_code:
        otp.attempts += 1
        if otp.attempts >= 3:
            otp.is_used = True
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
        )

    # Mark OTP as used
    otp.is_used = True
    otp.verified_at = datetime.now(timezone.utc)
    await db.commit()

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Create session
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)
    session = UserSession(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        is_active=True,
    )
    db.add(session)
    await db.commit()

    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_expiration_hours * 3600,
        ),
        session_id=session.id,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout User",
    description="Invalidate current session",
)
async def logout_user(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Logout user by invalidating their session."""
    try:
        session_id = UUID(request.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format",
        )

    stmt = select(UserSession).where(UserSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    session.is_active = False
    await db.commit()

    return MessageResponse(message="Logged out successfully")
