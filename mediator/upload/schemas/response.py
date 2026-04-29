from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from mediator.upload.model import UploadSource, UploadStatus

class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: UploadSource
    status: UploadStatus
    message_count: int
    created_at: datetime
