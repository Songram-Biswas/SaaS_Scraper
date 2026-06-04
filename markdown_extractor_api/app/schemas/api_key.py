from pydantic import BaseModel, UUID4
from datetime import datetime

class ApiKeyCreate(BaseModel):
    name: str = "Default Key"

class ApiKeyResponse(BaseModel):
    id: UUID4
    name: str
    prefix: str
    requests_used: int
    request_limit: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyGenerateResponse(BaseModel):
    message: str
    raw_api_key: str
    prefix: str
    warning: str = "Please copy this key immediately. You will not be able to see it again."