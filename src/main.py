from fastapi import FastAPI, Depends, File, UploadFile
from utils.jwt_token_manager import JwtTokenManger
from utils.base_postgres_orm import base_postgres_orm
from routes.auth import AuthRouter
from routes.videos import VideosRouter
from utils.raw_video_manager import raw_videos_manager
from datetime import datetime
from fastapi import HTTPException, status
from utils.aws_manager import AWSManager
from schemas.schemas import UrlResponse, UrlPayload

# *** YOUTUBE CLONE API ***

api: FastAPI = FastAPI()

# all routers objects
auth_router: AuthRouter = AuthRouter()
videos_router: VideosRouter = VideosRouter()

api.include_router(auth_router.router)
api.include_router(videos_router.router)

token_manager: JwtTokenManger = JwtTokenManger()
aws_manager: AWSManager = AWSManager()

# general routes


@api.post('/upload_raw_video')
async def upload_raw_video(file: UploadFile = File(...), auth_data: dict = Depends(token_manager.get_current_user)):
    video_bytes: bytes = await file.read()
    key: str = raw_videos_manager.add_video(video_bytes)

    return {
        'upload_key': key,
        'created_at': str(datetime.now())
    }


@api.post('/link', response_model=UrlResponse)
def get_link(url_payload: UrlPayload, auth_data: dict = Depends(token_manager.get_current_user)):
    try:
        url: str = aws_manager.generate_link(
            object_name=url_payload.object_uri, for_video=url_payload.for_video)

        return {
            'url': url,
            'expiration_in_minutes': 60
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            'error': str(e)
        })


@api.get('/')
def root():
    return 'Youtube Clone API:::: access docs at API_URL/docs'


@api.on_event('startup')
def init_db():
    base_postgres_orm.make_schemas()
