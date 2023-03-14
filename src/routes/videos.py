from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session
from utils.jwt_token_manager import JwtTokenManger
from utils.base_postgres_orm import base_postgres_orm
from databases.videos_manager import VideosManager


class VideosRouter:

    def __init__(self) -> None:
        self.__router: APIRouter = APIRouter(prefix='/videos', tags=['Videos'])
        self.__token_manager = JwtTokenManger()

        # register route
        self.__register_routes()

    @property
    def router(self) -> APIRouter:
        return self.__router

    def __register_routes(self) -> None:

        @self.__router.get('/all')
        def videos(db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            return auth_data

        @self.__router.websocket('/upload')
        async def upload(websocket: WebSocket, db: Session = Depends(base_postgres_orm.db)):
            await websocket.accept()

            headers: dict = dict(websocket.headers)
            manager = VideosManager(db=db, headers=headers)

            # get video data
            video_data = await websocket.receive_json()

            await manager.process_video(
                video_data, websocket=websocket)

            await websocket.send_json({'is_completed': True})