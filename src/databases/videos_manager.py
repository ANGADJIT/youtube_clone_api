from sqlalchemy.orm import Session
from utils.aws_manager import AWSManager
from utils.jwt_token_manager import JwtTokenManger
from fastapi.websockets import WebSocket
from fastapi import HTTPException, status
from utils.constants import videos_quality_list, quality
from utils.temporary_files_manager import TemporaryFilesManager
from moviepy.editor import VideoFileClip
from schemas.schemas import VideoCreate
from utils.raw_video_manager import raw_videos_manager
from models.models import Videos
from uuid import uuid4
from typing import List
from models.models import Subscription
from sqlalchemy import and_
from models.models import UserInfo
from utils.enums import VideoType


class VideosManager:

    def __init__(self, db: Session, headers: dict, for_websocket: bool = True) -> None:
        self.__db = db
        self.__aws = AWSManager()
        self.__token_manager = JwtTokenManger()
        self.__files_manager = TemporaryFilesManager('assets/tempfiles')

        if for_websocket:
            self.__user_id: str = self.__authorize_user(headers)

    def __authorize_user(self, headers: dict) -> str:

        if 'authorization' not in list(headers.keys()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={'error': 'Bearer token required'})

        token: str = headers['authorization']
        auth_data: dict = self.__token_manager.get_current_user(token)

        return auth_data['user_id']

    def __add_video_data(self, video_model: VideoCreate, videos_uris: dict):

        video_data: dict = {
            'video_name': video_model.video_name,
            'video_1080p_s3_uri': videos_uris.get('1080P'),
            'video_720p_s3_uri': videos_uris.get('720P'),
            'video_480p_s3_uri': videos_uris.get('480P'),
            'video_360p_s3_uri': videos_uris.get('360P'),
            'video_240p_s3_uri': videos_uris.get('240P'),
            'video_144p_s3_uri': videos_uris.get('144P'),
            'thumbnail_s3_uri': videos_uris.get('thumbnail_s3_uri'),
            'user_id': self.__user_id,
            'video_description': video_model.description,
            'video_type': str(video_model.video_type),
        }

        video = Videos(**video_data)

        self.__db.add(video)
        self.__db.commit()

    async def process_video(self, video_data: dict, websocket: WebSocket) -> dict:

        try:
            video_model: VideoCreate = VideoCreate(**video_data)

        except:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={
                                'error': 'payload is not correct'})

        # all video processing functions

        def get_video_convertions_data(video: bytes) -> dict:
            file_name: str = self.__files_manager.write_data(
                video, is_binary=True)

            video_file = VideoFileClip(file_name)
            resolution: tuple = tuple(video_file.size)

            if 1080 in resolution or 1920 in resolution:
                resolution = (1080, 1920)
            elif 720 in resolution or 1280 in resolution:
                resolution = (1280, 720)
            elif 480 in resolution or 854 in resolution:
                resolution = (480, 854)
            elif 360 in resolution or 640 in resolution:
                resolution = (640, 360)
            elif 240 in resolution or 426 in resolution:
                resolution = (426, 240)
            elif 144 in resolution or 256 in resolution:
                resolution = (256, 144)

            video_file.close()

            return {
                'convertions': videos_quality_list[resolution],
                'file_name': file_name,
                'actual_resolution': resolution
            }

        async def convert_videos(video_data: dict) -> None:

            # open file in bytes
            video_id: str = str(uuid4())

            # upload thumbnail
            thumbnail: bytes | None = raw_videos_manager.get_video(
                video_model.thumbnail_upload_key)

            if thumbnail is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                    'error': 'invalid thumbnail upload key'})

            thumbnail_s3_uri: str = f'{self.__user_id}/thumbanails/{video_id}/thumbnail.png'

            self.__aws.upload_file(file=thumbnail, key=thumbnail_s3_uri)

            # list of all uris
            videos_uris: dict = {
                '1080P': None,
                '720P': None,
                '480P': None,
                '360P': None,
                '240P': None,
                '144P': None,
                'thumbnail_s3_uri': thumbnail_s3_uri
            }

            file_name: str = video_data['file_name']
            convertions: list[tuple] = video_data['convertions']
            actual_resolution: tuple = video_data['actual_resolution']

            # before converting upload actual video
            actual_video_s3_uri: str = f'{self.__user_id}/videos/{video_id}/{quality[actual_resolution]}.mp4'
            videos_uris[quality[actual_resolution]] = actual_video_s3_uri
            actual_video: bytes | None = raw_videos_manager.get_video(
                video_model.video_upload_key)

            self.__aws.upload_file(file=actual_video, key=actual_video_s3_uri)

            with VideoFileClip(file_name) as vid:

                for resolution in convertions:
                    converted_video = vid.resize(resolution)
                    path: str = f'assets/tempfiles/{quality[resolution]}.mp4'
                    converted_video.write_videofile(
                        path,
                        codec="libx264",
                        audio_codec="aac",
                        remove_temp=True,
                        logger=None,
                    )

                    key: str = f'{self.__user_id}/videos/{video_id}/{quality[resolution]}.mp4'

                    with open(path, 'rb') as file:
                        self.__aws.upload_file(
                            file=file.read(), key=key)

                    videos_uris[quality[resolution]] = key

                    await websocket.send_json({'video_resolution': quality[resolution], 'is_processed': True})

            # now add all data
            self.__add_video_data(video_model=video_model,
                                  videos_uris=videos_uris)

        # get convertion data
        video: bytes = raw_videos_manager.get_video(
            video_model.video_upload_key)

        if video is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                'error': 'invalid video upload key'})

        if video is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                'upload_key not found'})

        data: dict = get_video_convertions_data(video)

        await convert_videos(video_data=data)

    # get all videos
    def get_all(self) -> list[Videos]:
        videos: List[Videos] = self.__db.query(Videos).all()

        return videos

    def subscribe(self, subscription_data: dict) -> None:
        subscription: Subscription | None = self.__db.query(Subscription).filter(and_(Subscription.user_subscribed_to ==
                                                                                      subscription_data['user_subscribed_to'], Subscription.user_who_subcribed == subscription_data['user_who_subcribed'])).first()

        if subscription is None:
            subscription: Subscription = Subscription(**subscription_data)

            self.__db.add(subscription)
            self.__db.commit()

        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
                'error': 'Already subscribed'})

    def is_subscribed(self, subscription_data: dict) -> bool:
        subscription: Subscription | None = self.__db.query(Subscription).filter(and_(Subscription.user_subscribed_to ==
                                                                                      subscription_data['user_subscribed_to'], Subscription.user_who_subcribed == subscription_data['user_who_subcribed'])).first()

        if subscription is None:
            return False
        else:
            return True

    def get_subscription_count(self, user_subscribed_to: str) -> int:
        try:
            count: int = self.__db.query(Subscription).filter(
                Subscription.user_subscribed_to == user_subscribed_to).count()
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                'error': 'ID not found'})

        return count

    def like_video(self, video_id: str) -> None:
        video = self.__db.query(Videos).filter(Videos.id == video_id)

        if video is not None:
            video_copy: dict = video.first().as_dict()

            video_copy['video_likes'] += 1

            video.update(video_copy, synchronize_session=False)
            self.__db.commit()

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                'error': 'Video ID not found'})

    def get_channel_info(self, user_id: str) -> dict:
        try:
            user_info: UserInfo = self.__db.query(
                UserInfo).filter(UserInfo.id == user_id).first()

            return {
                'channel_name': user_info.channel_name,
                'profile_url': self.__aws.generate_link(user_info.profile_s3_uri, for_video=False)
            }

        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                'error': 'User ID not found'})

    def get_videos_recommendations(self, video_type: str) -> list[Videos]:

        try:
            # just for verification
            VideoType(video_type)

            videos: List[Videos] = self.__db.query(Videos).filter(
                Videos.video_type == video_type).all()

            return videos

        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                'error': 'Video TYPE not found'})

    def search(self, search_pattern: str) -> list[Videos]:
        videos: List[Videos] = self.__db.query(Videos).filter(
            Videos.video_name.like(f'%{search_pattern}%')).all()

        return videos

    def get_subscription_videos(self, user_who_subscribed: str) -> list[Videos]:

        subscription_videos: List[Videos] = self.__db.query(Videos).filter(
            Videos.user_id.in_(
                self.__db.query(Subscription.user_subscribed_to).filter(
                    Subscription.user_who_subcribed == user_who_subscribed)
            )
        ).all()

        return subscription_videos

    def get_user_profile(self, user_id: str) -> str:
        uri: str = self.__db.query(UserInfo).filter(
            UserInfo.id == user_id).first().profile_s3_uri

        return self.__aws.generate_link(object_name=uri, for_video=False)

    def get_likes(self, video_id: str) -> int:
        video: Videos = self.__db.query(Videos).filter(
            Videos.id == video_id).first()

        if video is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                'error': 'Video ID not found'})

        return video.video_likes


