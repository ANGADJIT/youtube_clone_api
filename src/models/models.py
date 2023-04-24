import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, TIMESTAMP


Base: DeclarativeMeta = declarative_base()


class UserInfo(Base):

    __tablename__ = 'UserInfo_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, comment='user email')
    password = Column(String, unique=False, nullable=False,
                      comment='user password')
    channel_name = Column(String, unique=False, nullable=False,
                          comment='user channel name')
    profile_s3_uri = Column(String, unique=True,
                            nullable=True, comment='profile pic')


class Comments(Base):

    __tablename__ = 'Comments_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment = Column(String, unique=False, nullable=False,
                     comment='user comment')
    commented_at = Column(TIMESTAMP, server_default='NOW()',
                          comment='user comment time')


class Videos(Base):

    __tablename__ = 'Videos_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_name = Column(String, unique=True, nullable=False,
                        comment='name of the video')
    user_id = Column(UUID, ForeignKey('UserInfo_Entity.id'),
                     comment='user id', nullable=False)
    video_1080p_s3_uri = Column(
        String, unique=False, nullable=True, comment='1080p quality video s3 uri')
    video_720p_s3_uri = Column(
        String, unique=False, nullable=True, comment='720p quality video s3 uri')
    video_480p_s3_uri = Column(
        String, unique=False, nullable=True, comment='480p quality video s3 uri')
    video_360p_s3_uri = Column(
        String, unique=False, nullable=True, comment='360p quality video s3 uri')
    video_240p_s3_uri = Column(
        String, unique=False, nullable=True, comment='240p quality video s3 uri')
    video_144p_s3_uri = Column(
        String, unique=False, nullable=True, comment='144p quality video s3 uri')
    video_description = Column(
        String, unique=False, nullable=False, comment='description of the video')
    video_likes = Column(Integer, unique=False, nullable=False,
                         default=0, comment='likes on the video')
    video_type = Column(Enum('MUSIC', 'DANCE', 'COMEDY', 'INFORMATIONAL',
                        'EDUCATIONAL', 'HEALTH_CARE', name='video_type'), comment='type of the video')
    thumbnail_s3_uri = Column(
        String, unique=True, nullable=False, comment='thumbnail of the video')
    comments_id = Column(UUID, ForeignKey(
        'Comments_Entity.id'), comment='comments on the video')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Subscription(Base):

    __tablename__ = 'Subsription_Entity'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_subscribed_to = Column(UUID, ForeignKey(
        'UserInfo_Entity.id'), nullable=False, comment='user whose channel is subscribed')
    user_who_subcribed = Column(UUID, ForeignKey(
        'UserInfo_Entity.id'), nullable=False, comment='user who is subscribing the channel')
