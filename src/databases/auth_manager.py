from sqlalchemy.orm import Session
from utils.aws_manager import AWSManager
from models.models import UserInfo
from datetime import datetime
from utils.jwt_token_manager import JwtTokenManger


class AuthManager:

    def __init__(self, db: Session) -> None:
        self.__db = db
        self.__aws = AWSManager()
        self.__token_manager = JwtTokenManger()

    def register_login(self, auth_data: dict) -> dict:

        # check the user is there or not
        check = self.__db.query(UserInfo).filter(
            UserInfo.email == auth_data['email']).first()

        if check is None:
            # make None profile photo in copy data

            auth_user: UserInfo = UserInfo(**auth_data)

            self.__db.add(auth_user)
            self.__db.commit()

            # get user id
            user = self.__db.query(UserInfo).filter(
                UserInfo.email == auth_data['email']).first()

            # generate access token
            access_token: str = self.__token_manager.generate_jwt_token(
                {'user_id': user.id})

            return {
                'access_token': access_token,
                'created_at': str(datetime.now())
            }
        
        # TODO :: ANMOL IMPLEMENT LOGIN LOGIC HERE
        else:
            pass