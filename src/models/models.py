import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, TIMESTAMP


Base: DeclarativeMeta = declarative_base()


class UserInfo(Base):

    __tablename__ = 'UserInfo_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=False, nullable=False)
    profile_s3_uri = Column(String, unique=True, nullable=False)


class Comments(Base):

    __tablename__ = 'Comments_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment = Column(String, unique=False, nullable=False)
    commented_at = Column(TIMESTAMP, server_default='NOW()')


class Videos(Base):

    __tablename__ = 'Videos_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_name = Column(String, unique=True, nullable=False)
    video_1080p_s3_uri = Column(String, unique=False, nullable=True)
    video_720p_s3_uri = Column(String, unique=False, nullable=True)
    video_480p_s3_uri = Column(String, unique=False, nullable=True)
    video_360p_s3_uri = Column(String, unique=False, nullable=True)
    video_240p_s3_uri = Column(String, unique=False, nullable=True)
    video_144p_s3_uri = Column(String, unique=False, nullable=True)
    video_description = Column(String, unique=False, nullable=False)
    video_likes = Column(Integer, unique=False, nullable=False, default=0)
    video_type = Column(Enum('MUSIC', 'DANCE', 'COMEDY', 'INFORMATIONAL',
                        'EDUCATIONAL', 'HEALTH_CARE', name='video_type'))
    thumbnail_s3_uri = Column(String, unique=True, nullable=False)
    comments_id = Column(UUID, ForeignKey('Comments_Entity.id'))


class Subscription(Base):

    __tablename__ = 'Subsription_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_subscribed_to = Column(UUID, ForeignKey(
        'UserInfo_Entity.id'), nullable=False)
    user_who_subcribed = Column(UUID, ForeignKey(
        'UserInfo_Entity.id'), nullable=False)
