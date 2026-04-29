import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from mediator.upload.model import UploadSource
from mediator.upload.service import UploadService
from mediator.upload.schemas.response import UploadResponse
from mediator.message.schemas.response import MessageResponse

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
)

@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a chat export",
    description="Upload a .txt export from WhatsApp or other sources for parsing."
)
async def upload_chat(
    file: UploadFile = File(...),
    source: UploadSource = Form(default=UploadSource.WHATSAPP),
    # Optional user_id if we want to tie it to a logged in user later
    user_id: uuid.UUID | None = Form(default=None),
    db: AsyncSession = Depends(get_db)
) -> UploadResponse:
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt files are supported currently."
        )

    try:
        upload = await UploadService.process_upload(db, file, source, user_id)
        return upload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}"
        )

@router.get(
    "/{upload_id}/messages",
    response_model=List[MessageResponse],
    summary="Get parsed messages",
    description="Retrieve all parsed messages for a specific upload."
)
async def get_messages(
    upload_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> List[MessageResponse]:
    messages = await UploadService.get_upload_messages(db, upload_id)
    return messages
