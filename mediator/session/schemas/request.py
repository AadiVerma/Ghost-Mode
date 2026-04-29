from pydantic import BaseModel
import uuid

class CreateSessionRequest(BaseModel):
    persona_id: uuid.UUID

class SendMessageRequest(BaseModel):
    content: str
