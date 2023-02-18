from pydantic import BaseModel, EmailStr
from typing import Optional


class AuthCreate(BaseModel):
    email: EmailStr
    password: str
    channel_name: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    created_at: str
