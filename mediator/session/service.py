import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from mediator.session.model import Session, SessionMessage, SessionStatus, SessionRole
from mediator.persona.model import Persona, PersonaStatus

class SessionService:
    @staticmethod
    async def create_session(db: AsyncSession, persona_id: uuid.UUID, user_id: uuid.UUID | None = None) -> Session:
        # Verify persona exists and is ready
        stmt = select(Persona).where(Persona.id == persona_id)
        result = await db.execute(stmt)
        persona = result.scalar_one_or_none()

        if not persona:
            raise ValueError("Persona not found.")
        if persona.status != PersonaStatus.READY:
            raise ValueError("Persona is not yet ready.")

        # Create session
        session = Session(
            user_id=user_id,
            persona_id=persona_id,
            status=SessionStatus.ACTIVE
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session

    @staticmethod
    async def get_session(db: AsyncSession, session_id: uuid.UUID) -> Session | None:
        stmt = select(Session).where(Session.id == session_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_session_messages(db: AsyncSession, session_id: uuid.UUID) -> list[SessionMessage]:
        stmt = select(SessionMessage).where(SessionMessage.session_id == session_id).order_by(SessionMessage.created_at)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def send_message(db: AsyncSession, session_id: uuid.UUID, content: str) -> SessionMessage:
        from ai.client import generate_chat_response
        from ai.prompts import PERSONA_CHAT_SYSTEM_PROMPT

        session = await SessionService.get_session(db, session_id)
        if not session:
            raise ValueError("Session not found.")
        if session.status != SessionStatus.ACTIVE:
            raise ValueError("Session is no longer active.")

        # Save user message
        user_msg = SessionMessage(
            session_id=session_id,
            role=SessionRole.USER,
            content=content
        )
        db.add(user_msg)
        await db.commit()

        # Fetch Persona
        stmt = select(Persona).where(Persona.id == session.persona_id)
        result = await db.execute(stmt)
        persona = result.scalar_one()

        # Build System Prompt
        vs = persona.voice_signature or {}
        system_prompt = PERSONA_CHAT_SYSTEM_PROMPT.format(
            age_range=persona.age_range,
            tone=vs.get("tone", ""),
            phrases=", ".join(vs.get("recurring_phrases", [])),
            punctuation=vs.get("punctuation_style", ""),
            emojis=vs.get("emoji_habits", ""),
            themes=", ".join(persona.themes or []),
            beliefs=", ".join(persona.beliefs or []),
            fears=", ".join(persona.fears or []),
            samples="\n".join(persona.sample_messages or [])
        )

        # Build Chat History
        all_msgs = await SessionService.get_session_messages(db, session_id)
        chat_history = [{"role": msg.role.value, "content": msg.content} for msg in all_msgs]

        # Call AI
        ai_response_text = await generate_chat_response(system_prompt, chat_history)

        # Save Assistant message
        asst_msg = SessionMessage(
            session_id=session_id,
            role=SessionRole.ASSISTANT,
            content=ai_response_text
        )
        db.add(asst_msg)
        await db.commit()
        await db.refresh(asst_msg)

        return asst_msg
