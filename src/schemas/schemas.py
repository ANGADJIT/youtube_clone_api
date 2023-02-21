from pydantic import BaseModel, EmailStr
from typing import Optional


class AuthCreate(BaseModel):
    email: EmailStr
    password: str
    channel_name: str


class AuthResponse(BaseModel):
    access_token: str
    created_at: str

    class Config:
        orm_mode = True
