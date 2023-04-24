from pydantic import BaseModel, EmailStr
from utils.enums import VideoType
from uuid import UUID
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


class VideoResponse(BaseModel):

    id: UUID
    video_name: str
    user_id: UUID
    video_1080p_s3_uri: str = None
    video_720p_s3_uri:  str = None
    video_480p_s3_uri:  str = None
    video_360p_s3_uri:  str = None
    video_240p_s3_uri:  str = None
    video_144p_s3_uri:  str = None
    video_description:  str = None
    video_likes: int
    video_type: str
    thumbnail_s3_uri: str
    comments_id: str = None

    class Config:
        orm_mode = True


class UrlPayload(BaseModel):
    object_uri: str
    for_video: bool = True


class UrlResponse(BaseModel):

    url: str
    expiration_in_minutes: int


class SubscriptionCheck(BaseModel):
    is_subscribed: bool

class SubscriptionCount(BaseModel):
    count: int
    counted_at: str