from pydantic import BaseModel, ConfigDict
import uuid
from typing import List, Optional
from datetime import datetime
from mediator.session.model import SessionStatus, SessionRole

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    persona_id: uuid.UUID
    status: SessionStatus
    created_at: datetime

class SessionMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    role: SessionRole
    content: str
    created_at: datetime
