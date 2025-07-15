from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    key: str
    name: str
    created_at: datetime
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool

    class Config:
        from_attributes = True

class BackgroundRemovalResponse(BaseModel):
    success: bool
    message: str
    processed_image_url: Optional[str] = None
    processing_time: Optional[float] = None
    model_used: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool
    error: str
    details: Optional[str] = None
