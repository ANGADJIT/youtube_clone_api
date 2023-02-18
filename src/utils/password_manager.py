from passlib.context import CryptContext


class PasswordManager:

    def __init__(self) -> None:
        self.__pwd_context = CryptContext(
            schemes=['bcrypt'], deprecated='auto')

    def hash_password(self, password: str) -> str:
        return self.__pwd_context.hash(password)

    def verify_password(self, user_password: str, actual_password: str) -> bool:
        return self.__pwd_context.verify(user_password, actual_password)
