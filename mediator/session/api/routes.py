import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from mediator.session.service import SessionService
from mediator.session.schemas.request import CreateSessionRequest, SendMessageRequest
from mediator.session.schemas.response import SessionResponse, SessionMessageResponse

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)

@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a Session",
    description="Initialize a new chat session with an extracted Persona."
)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    try:
        session = await SessionService.create_session(
            db=db,
            persona_id=request.persona_id
        )
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get Session info",
    description="Retrieve details about a specific chat session."
)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    session = await SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found."
        )
    return session

@router.get(
    "/{session_id}/messages",
    response_model=List[SessionMessageResponse],
    summary="Get Session Messages",
    description="Retrieve the chat history for a session."
)
async def get_session_messages(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> List[SessionMessageResponse]:
    # Ensure session exists first to return 404 properly if needed
    session = await SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found."
        )

    messages = await SessionService.get_session_messages(db, session_id)
    return messages

@router.post(
    "/{session_id}/messages",
    response_model=SessionMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message",
    description="Send a message to the persona and receive their reply."
)
async def send_message(
    session_id: uuid.UUID,
    payload: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
) -> SessionMessageResponse:
    try:
        reply = await SessionService.send_message(db, session_id, payload.content)
        return reply
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )
