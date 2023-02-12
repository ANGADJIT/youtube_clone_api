import jwt
from jwt import PyJWTError
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from datetime import datetime
import time
from utils.config import Enviroments
from fastapi.security import OAuth2PasswordBearer

schema = OAuth2PasswordBearer(tokenUrl='auth/register-login')


class JwtTokenManger:

    def __init__(self) -> None:
        self.__enviroments = Enviroments()

    def generate_jwt_token(self, data: dict) -> str:
        data_to_be_encoded: dict = data.copy()

        data_to_be_encoded['exp'] = datetime.utcnow(
        ) + timedelta(minutes=int(self.__enviroments.access_token_expires_minutes))

        return jwt.encode(data_to_be_encoded, self.__enviroments.secret_key, algorithm=self.__enviroments.algorithm)

    def __verify_token(self, token: str, credential_exception: Exception, expiration_exception: Exception) -> dict:

        try:
            payload: dict = jwt.decode(token, self.__enviroments.secret_key, algorithms=[
                                       self.__enviroments.algorithm])

            if len(list(payload.keys())) == 1:
                raise credential_exception

            elif self.__check_token_expiration(payload['exp']):
                raise expiration_exception

            return payload

        except PyJWTError:
            raise credential_exception

    def __check_token_expiration(self, exp: timedelta) -> bool:
        return exp < time.time()

    def get_current_user(self, token: str = Depends(schema)) -> dict:
        credentials_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='could not validate the credentails', headers={'WWW-Authenticate': 'bearer'})

        expiration_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='token expired')

        return self.__verify_token(token, credentials_exception, expiration_exception=expiration_exception)