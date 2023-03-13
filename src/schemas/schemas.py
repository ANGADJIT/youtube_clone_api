from pydantic import BaseModel, EmailStr
from utils.enums import VideoType

# for Auth


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

# for Videos


class VideoCreate(BaseModel):

    video_upload_key: str
    thumbnail_upload_key: str
    description: str
    video_type: VideoType
    video_name: str
