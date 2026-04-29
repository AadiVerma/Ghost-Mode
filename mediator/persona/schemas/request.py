from pydantic import BaseModel, Field
import uuid

class CreatePersonaRequest(BaseModel):
    upload_id: uuid.UUID
    age_range: str = Field(..., max_length=32, description="e.g. '17-19'")
