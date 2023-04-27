from fastapi import APIRouter, Depends, Response, status, Query
from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session
from models.models import Videos
from schemas.schemas import ChannelNameResponse, ChannelProfileResponse, UserProfileResponse, VideoResponse, SubscriptionCheck, SubscriptionCount, UserChannelResponse, Likes
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

        @self.__router.post('/like/{video_id}')
        def like_video(video_id: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            manager.like_video(video_id=video_id, user_id=auth_data['user_id'])

            return Response(status_code=status.HTTP_204_NO_CONTENT)

        @self.__router.get('/channel_info/{user_id}', response_model=UserChannelResponse)
        def get_channel_info(user_id: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            user_info: dict = manager.get_channel_info(user_id=user_id)

            return user_info

        @self.__router.get('/recommendations/{video_type}', response_model=List[VideoResponse])
        def get_videos_recommendations(video_type: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            recommendations: List[Videos] = manager.get_videos_recommendations(
                video_type=video_type)

            return recommendations

        @self.__router.get('/search', response_model=List[VideoResponse])
        def search(search_pattern: str = Query(min_length=1), db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            searched_videos: List[Videos] = manager.search(
                search_pattern=search_pattern)

            return searched_videos

        @self.__router.get('/subscription_videos')
        def get_subscription_videos(db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            subscription_videos: List[Videos] = manager.get_subscription_videos(
                user_who_subscribed=auth_data['user_id'])

            return subscription_videos

        @self.__router.get('/user_profile_photo', response_model=UserProfileResponse)
        def get_user_profile_photo(db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            url: str = manager.get_user_profile(user_id=auth_data['user_id'])

            return {
                'profile_url': url
            }

        @self.__router.get('/likes/{video_id}', response_model=Likes)
        def get_likes(video_id: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            likes: int = manager.get_likes(video_id=video_id)
            counted_at: str = str(datetime.now())

            return {
                'likes': likes,
                'counted_at': counted_at
            }

        @self.__router.get('/channel_profile/{user_id}', response_model=ChannelProfileResponse)
        def get_channel_profile(user_id: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            url: str = manager.get_user_profile(user_id=user_id)

            return {
                'profile_url': url
            }

        @self.__router.get('/channel_name/{user_id}', response_model=ChannelNameResponse)
        def get_channel_name(user_id: str, db: Session = Depends(base_postgres_orm.db), auth_data: dict = Depends(self.__token_manager.get_current_user)):
            manager = VideosManager(db=db, headers={}, for_websocket=False)

            channel_name: str = manager.get_channel_name(user_id=user_id)

            return {
                'channel_name': channel_name
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
