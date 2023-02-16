from pydantic import BaseModel, EmailStr
from typing import Optional


class AuthCreate(BaseModel):
    email: EmailStr
    password: str
    channel_name: Optional[str] = None
    profile_photo: Optional[bytes] = None


class AuthResponse(BaseModel):
    access_token: str
    created_at: str
