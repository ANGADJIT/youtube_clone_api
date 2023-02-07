from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm.decl_api import DeclarativeMeta
from config import Enviroments


class BasePostgresORM:

    Base: DeclarativeMeta = declarative_base()

    _instance = None

    def __init__(self) -> None:
        # load env's and init sql alchemy engine
        enviroments = Enviroments()

        DATABASE_URL = f'postgresql://{enviroments.database_user}:{enviroments.database_password}@{enviroments.database_host}/{enviroments.database_name}'
        engine: Engine = create_engine(DATABASE_URL)
        self.__session_local: function = sessionmaker(
            bind=engine, autoflush=False, autocommit=False)

        self.Base.metadata.create_all(bind=engine)

    def __get_db(self) -> None:
        db = self.__session_local()

        try:
            yield db
        finally:
            db.close()

    # database object getter
    @property
    def db(self) -> function:
        return self.__get_db

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
