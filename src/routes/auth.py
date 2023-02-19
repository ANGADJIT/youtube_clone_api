from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from databases.auth_manager import AuthManager
from schemas.schemas import AuthCreate, AuthResponse
from sqlalchemy.orm import Session
from utils.base_postgres_orm import base_postgres_orm


class AuthRouter:

    def __init__(self) -> None:
        self.__router: APIRouter = APIRouter(prefix='/auth', tags=['Auth'])

        # register routes
        self.__register_routes()

    # getter for router object
    @property
    def router(self) -> APIRouter:
        return self.__router

    def __register_routes(self) -> None:

        @self.__router.post('/register', status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
        def register(auth: AuthCreate = Depends(), file: UploadFile = File(...), db: Session = Depends(base_postgres_orm.db)):
            auth_manager = AuthManager(db)

            result: dict | None = auth_manager.register(
                auth_data=auth.dict(), file=file.file)

            if result is None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
                                    'error': f'user with {auth.email} already exists'})

            return result

        @self.__router.post('/login', status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
        def login(auth: AuthCreate = Depends(), db: Session = Depends(base_postgres_orm.db)):
            auth_manager = AuthManager(db)

            result: dict | None = auth_manager.login(auth_data=auth.dict())
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                    'error': 'email or password is invalid'
                })
            return result
