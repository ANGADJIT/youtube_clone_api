from fastapi import FastAPI
from utils.base_postgres_orm import base_postgres_orm

# *** YOUTUBE CLONE API ***

api: FastAPI = FastAPI()


@api.get('/')
def root():
    return 'Youtube Clone API:::: access docs at API_URL/docs'


@api.on_event('startup')
def init_db():
    base_postgres_orm.make_schemas()
