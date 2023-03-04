from sqlalchemy.orm import Session
from utils.aws_manager import AWSManager
from utils.jwt_token_manager import JwtTokenManger
from fastapi.websockets import WebSocket
from fastapi import HTTPException, status


class VideosManager:

    def __init__(self, db: Session, headers: dict) -> None:
        self.__db = db
        self.__aws = AWSManager()
        self.__token_manager = JwtTokenManger()

        self.__user_id: str = self.__authorize_user(headers)

    def __authorize_user(self, headers: dict) -> str:

        if 'authorization' not in list(headers.keys()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={'error': 'Bearer token required'})

        token: str = headers['authorization']
        auth_data: dict = self.__token_manager.get_current_user(token)

        return auth_data['user_id']

    # TODO : @Aasha make a function to process video
    def process_video(self, video: bytes, websocket: WebSocket) -> dict:
        videos_data = {}

        # 1 check the resolution of video

        # 2 acc to resolution map all the outputs

        # 3 return the map
