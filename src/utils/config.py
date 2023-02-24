from pydantic import BaseSettings


class Enviroments(BaseSettings):

    server_type: str

    database_host: str
    database_user: str
    database_password: str
    database_port: str
    database_name: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: str

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region_name: str
    s3_bucket_name: str

    class Config:
        env_file = '.env'
