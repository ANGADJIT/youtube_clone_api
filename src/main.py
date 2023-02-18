from fastapi import FastAPI
from utils.base_postgres_orm import base_postgres_orm
from routes.auth import AuthRouter

# *** YOUTUBE CLONE API ***

api: FastAPI = FastAPI()

# all routers objects
auth_router: AuthRouter = AuthRouter()

api.include_router(auth_router.router)


@api.get('/')
def root():
    return 'Youtube Clone API:::: access docs at API_URL/docs'


@api.on_event('startup')
def init_db():
    base_postgres_orm.make_schemas()
