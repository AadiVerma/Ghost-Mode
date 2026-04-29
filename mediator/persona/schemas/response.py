from pydantic import BaseModel, ConfigDict
import uuid
from typing import Optional, List, Dict
from mediator.persona.model import PersonaStatus

class PersonaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    upload_id: uuid.UUID
    age_range: str
    status: PersonaStatus

    voice_signature: Optional[Dict] = None
    themes: Optional[List[str]] = None
    beliefs: Optional[List[str]] = None
    fears: Optional[List[str]] = None
    relationships: Optional[Dict] = None
    sample_messages: Optional[List[str]] = None
