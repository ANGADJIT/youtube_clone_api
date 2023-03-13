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


class VideosManager:

    def __init__(self, db: Session, headers: dict) -> None:
        self.__db = db
        self.__aws = AWSManager()
        self.__token_manager = JwtTokenManger()
        self.__files_manager = TemporaryFilesManager('assets/tempfiles')

        self.__user_id: str = self.__authorize_user(headers)

    def __authorize_user(self, headers: dict) -> str:

        if 'authorization' not in list(headers.keys()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={'error': 'Bearer token required'})

        token: str = headers['authorization']
        auth_data: dict = self.__token_manager.get_current_user(token)

        return auth_data['user_id']

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
                'file_name': file_name
            }

        async def convert_videos(video_data: list) -> dict:

            file_name: str = video_data['file_name']
            convertions: list[tuple] = video_data['convertions']

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

                    # opne file in bytes
                    with open(path, 'rb') as file:
                        self.__aws.upload_file(
                            file=file.read(), key=f'videos/{quality[resolution]}.mp4')

                    await websocket.send_json({'video_resolution': quality[resolution], 'is_processed': True})

            return video_data

        # get convertion data
        video: bytes = raw_videos_manager.get_video(
            video_model.video_upload_key)

        if video is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                'upload_key not found'})

        data: dict = get_video_convertions_data(video)

        # convert videos
        videos: dict = await convert_videos(video_data=data)

        return videos

