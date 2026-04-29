import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from mediator.persona.service import PersonaService
from mediator.persona.schemas.request import CreatePersonaRequest
from mediator.persona.schemas.response import PersonaResponse

router = APIRouter(
    prefix="/personas",
    tags=["personas"],
)

@router.post(
    "",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Extract a Persona",
    description="Extract a past-self Persona from an upload."
)
async def create_persona(
    request: CreatePersonaRequest,
    # Optional user_id dependency could go here
    db: AsyncSession = Depends(get_db)
) -> PersonaResponse:
    try:
        persona = await PersonaService.create_persona(
            db=db,
            upload_id=request.upload_id,
            age_range=request.age_range
        )
        return persona
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Persona extraction failed: {str(e)}"
        )

@router.get(
    "/{persona_id}",
    response_model=PersonaResponse,
    summary="Get a Persona",
    description="Retrieve the status and details of an extracted Persona."
)
async def get_persona(
    persona_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> PersonaResponse:
    persona = await PersonaService.get_persona(db, persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found."
        )
    return persona
