from sqlalchemy.orm import Session
from utils.aws_manager import AWSManager
from models.models import UserInfo
from datetime import datetime
from utils.password_manager import PasswordManager
from utils.jwt_token_manager import JwtTokenManger
from fastapi.security import OAuth2PasswordRequestForm


class AuthManager:

    def __init__(self, db: Session) -> None:
        self.__db = db
        self.__aws = AWSManager()
        self.__password_manager = PasswordManager()
        self.__token_manager = JwtTokenManger()

    def register(self, auth_data: dict, file: bytes) -> dict | None:

        # check if user exits
        check = self.__db.query(UserInfo).filter(
            UserInfo.email == auth_data['email'])

        if not check.first():

            # remove profile photo from copy data and add profile_s3_uri as None
            copy_data: dict = auth_data.copy()
            copy_data['profile_s3_uri'] = None

            # hash the password
            copy_data['password'] = self.__password_manager.hash_password(
                copy_data['password'])

            # add this to db
            user = UserInfo(**copy_data)

            self.__db.add(user)
            self.__db.commit()

            # get user id first
            user_info = self.__db.query(UserInfo).filter(
                UserInfo.email == auth_data['email'])

            # upload profile photo to s3
            s3_key: str = f'{user_info.first().id}/profile_pic/profile.png'

            self.__aws.upload_file(file=file, key=s3_key)

            # update user profile uri
            copy_data['profile_s3_uri'] = s3_key

            user_info.update(copy_data, synchronize_session=False)
            self.__db.commit()

            return {'user_id': user_info.first().id, 'created_at': str(datetime.now())}

        else:
            return None

    def login(self, auth_data: OAuth2PasswordRequestForm) -> dict | None:
        # get user
        user = self.__db.query(UserInfo).filter(
            UserInfo.email == auth_data.username).first()
        # if user is registered verify password and retrun access token with time otherwise return None
        if user:
            if self.__password_manager.verify_password(user_password=auth_data.password, actual_password=user.password):
                access_token: str = self.__token_manager.generate_jwt_token(data={
                    'user_id': str(user.id)
                })

                return {
                    'access_token': access_token,
                    'created_at': str(datetime.now())
                }
            else:
                return None
        else:
            return None
