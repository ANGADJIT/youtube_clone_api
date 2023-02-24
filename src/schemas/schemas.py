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


class RefreshToken(BaseModel):

    token: str
    user_id: str


class AuthCreatResponse(BaseModel):
    user_id: str
    created_at: str
