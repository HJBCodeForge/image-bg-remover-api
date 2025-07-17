from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

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
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    api_calls_count: int

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

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
