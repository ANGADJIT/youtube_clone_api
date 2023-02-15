from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from utils.config import Enviroments
from models.models import Base


class BasePostgresORM:
    _instance = None

    def __init__(self) -> None:
        # load env's and init sql alchemy engine
        self.__enviroments = Enviroments()

    def __get_db(self) -> None:
        db = self.__session_local()

        try:
            yield db
        finally:
            db.close()

    def make_schemas(self) -> None:
        DATABASE_URL = f'postgresql://{self.__enviroments.database_user}:{self.__enviroments.database_password}@{self.__enviroments.database_host}/{self.__enviroments.database_name}'
        self.__engine: Engine = create_engine(DATABASE_URL)
        self.__session_local: function = sessionmaker(
            bind=self.__engine, autoflush=False, autocommit=False)

        Base.metadata.create_all(bind=self.__engine)

    # database object getter
    @property
    def db(self):
        return self.__get_db


base_postgres_orm: BasePostgresORM = BasePostgresORM()
