import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from mediator.persona.model import Persona, PersonaStatus
from mediator.upload.service import UploadService
from mediator.persona.extractor import PersonaExtractor

class PersonaService:
    @staticmethod
    async def create_persona(db: AsyncSession, upload_id: uuid.UUID, age_range: str, user_id: uuid.UUID | None = None) -> Persona:
        # Create DB record
        persona = Persona(
            user_id=user_id,
            upload_id=upload_id,
            age_range=age_range,
            status=PersonaStatus.EXTRACTING
        )
        db.add(persona)
        await db.commit()
        await db.refresh(persona)

        # Get messages for upload
        all_messages = await UploadService.get_upload_messages(db, upload_id)
        
        if not all_messages:
            persona.status = PersonaStatus.FAILED
            await db.commit()
            raise ValueError("No messages found for the given upload_id.")

        # Extract (synchronous for now, per spec)
        persona = await PersonaExtractor.extract(persona, all_messages)
        
        await db.commit()
        await db.refresh(persona)
        
        return persona
        
    @staticmethod
    async def get_persona(db: AsyncSession, persona_id: uuid.UUID) -> Persona | None:
        stmt = select(Persona).where(Persona.id == persona_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
