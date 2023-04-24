from fastapi import APIRouter, Depends, Response, status
from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session
from models.models import Videos
from schemas.schemas import VideoResponse, SubscriptionCheck, SubscriptionCount
from utils.jwt_token_manager import JwtTokenManger
from utils.base_postgres_orm import base_postgres_orm
from databases.videos_manager import VideosManager
from typing import List
from datetime import datetime


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

        @self.__router.get('/all', response_model=List[VideoResponse])
        def videos(db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            videos: List[Videos] = manager.get_all()

            return videos

        @self.__router.post('/subscribe/{user_subscribed_to}')
        def subscribe(user_subscribed_to: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            manager.subscribe(subscription_data={
                'user_who_subcribed': auth_data['user_id'],
                'user_subscribed_to': user_subscribed_to
            })

            return Response(status_code=status.HTTP_204_NO_CONTENT)

        @self.__router.get('/check_subscription/{user_subscribed_to}', response_model=SubscriptionCheck)
        def check_subscription(user_subscribed_to: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            is_subscribed: bool = manager.is_subscribed(subscription_data={
                'user_who_subcribed': auth_data['user_id'],
                'user_subscribed_to': user_subscribed_to
            })

            return {'is_subscribed': is_subscribed}

        @self.__router.get('/get_subscription_count/{user_subscribed_to}', response_model=SubscriptionCount)
        def get_subscription_count(user_subscribed_to: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            count: int = manager.get_subscription_count(
                user_subscribed_to=user_subscribed_to)
            counted_at: str = str(datetime.now())

            return {
                'count': count,
                'counted_at': counted_at
            }

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
