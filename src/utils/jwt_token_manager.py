import jwt
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from datetime import datetime
import time
from utils.config import Enviroments
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, DecodeError

schema = OAuth2PasswordBearer(tokenUrl='auth/login')


class JwtTokenManger:

    def __init__(self) -> None:
        self.__enviroments = Enviroments()

    def generate_jwt_token(self, data: dict) -> str:
        data_to_be_encoded: dict = data.copy()

        data_to_be_encoded['exp'] = datetime.utcnow(
        ) + timedelta(minutes=int(self.__enviroments.access_token_expire_minutes))

        return jwt.encode(data_to_be_encoded, self.__enviroments.secret_key, algorithm=self.__enviroments.algorithm)

    def __verify_token(self, token: str, credential_exception: Exception, expiration_exception: Exception) -> dict:

        try:
            payload: dict = jwt.decode(token, self.__enviroments.secret_key, algorithms=[
                                       self.__enviroments.algorithm])

            return payload

        except DecodeError:
            raise credential_exception

        except ExpiredSignatureError:
            raise expiration_exception

    def get_current_user(self, token: str = Depends(schema)) -> dict:
        credentials_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='could not validate the credentails', headers={'WWW-Authenticate': 'bearer'})

        expiration_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='token expired')

        return self.__verify_token(token, credentials_exception, expiration_exception=expiration_exception)

    def refresh_token(self, token: str, user_id: str) -> dict | None:

        try:
            self.get_current_user(token=token)

            return None

        except HTTPException as e:

            if e.status_code == status.HTTP_404_NOT_FOUND:
                raise e

            elif e.status_code == status.HTTP_400_BAD_REQUEST:

                # generat new token
                new_token: str = self.generate_jwt_token(
                    data={'user_id': user_id})

                return {
                    'access_token': new_token,
                    'created_at': str(datetime.now())
                }

    def authorize_websocket(self, bearer_token: str) -> dict:
        # get token from header value
        token: str = bearer_token.split(' ')[1]

        # authorize user with token
        return self.get_current_user(token)
