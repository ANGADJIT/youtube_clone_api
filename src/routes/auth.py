from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response, status
from databases.auth_manager import AuthManager
from schemas.schemas import AuthCreate, AuthResponse, RefreshToken
from sqlalchemy.orm import Session
from utils.jwt_token_manager import JwtTokenManger
from fastapi.security import OAuth2PasswordRequestForm
from utils.base_postgres_orm import base_postgres_orm


class AuthRouter:

    def __init__(self) -> None:
        self.__router: APIRouter = APIRouter(prefix='/auth', tags=['Auth'])
        self.__token_manager = JwtTokenManger()

        # register routes
        self.__register_routes()

    # getter for router object
    @property
    def router(self) -> APIRouter:
        return self.__router

    def __register_routes(self) -> None:

        @self.__router.post('/register')
        def register(auth: AuthCreate = Depends(), file: UploadFile = File(...), db: Session = Depends(base_postgres_orm.db)):
            auth_manager = AuthManager(db)

            result: bool = auth_manager.register(
                auth_data=auth.dict(), file=file.file)

            if not result:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
                                    'error': f'user with {auth.email} already exists'})

            return Response(status_code=status.HTTP_201_CREATED)

        @self.__router.post('/login', status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
        def login(auth: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(base_postgres_orm.db)):
            auth_manager = AuthManager(db)

            result: dict | None = auth_manager.login(auth_data=auth)

            if result is None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                    'error': 'email or password is invalid'
                })

            return result

        @self.__router.post('/refresh', status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
        def refresh(refresh_data: RefreshToken):

            result: dict | None = self.__token_manager.refresh_token(
                token=refresh_data.token, user_id=refresh_data.user_id)
            if result is None:
                return Response(status_code=status.HTTP_409_CONFLICT)

            else:
                return result
        @self.__router.get('/dependent_test_route',status_code=status.HTTP_201_CREATED)
        def check_refresh(token:str):
                user: dict | None= self.__token_manager.get_current_user(token) 
                return user
            


