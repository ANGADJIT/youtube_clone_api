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
        
        if subscription is None:
            return  fa                                                                                                                                 subscription_data['user_subscribed_to'], Subscription.user_who_subcribed == subscription_data['user_who_subcribed'])).first()
