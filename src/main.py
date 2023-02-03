from fastapi import FastAPI

# *** YOUTUBE CLONE API ***

api: FastAPI = FastAPI()

@api.get('/')
def root():
    return 'Youtube Clone API:::: access docs at API_URL/docs'

