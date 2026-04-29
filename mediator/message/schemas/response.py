from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: datetime
    sender: str
    content: str
    is_media: bool
