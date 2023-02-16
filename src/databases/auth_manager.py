from sqlalchemy.orm import Session
from utils.aws_manager import AWSManager
from models.models import UserInfo
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
            data = auth_data.copy()
            data.update('profile_photo', None)

            auth_user: UserInfo = UserInfo(**data)

            self.__db.add(auth_data)
            self.__db.commit()
