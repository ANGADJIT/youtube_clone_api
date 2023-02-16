import boto3
from utils.config import Enviroments


class AWSManager:

    def __init__(self) -> None:
        self.__enviroments = Enviroments()

        # aws cred init
        if self.__enviroments.server_type == 'DEV':
            self.__s3 = boto3.client('s3',
                                     endpoint_url='http://localhost:9000',
                                     aws_access_key_id=self.__enviroments.aws_access_key_id,
                                     aws_secret_access_key=self.__enviroments.aws_secret_access_key)

        else:
            self.__s3 = boto3.client('s3',
                                     aws_access_key_id=self.__enviroments.aws_access_key_id,
                                     region_name=self.__enviroments.aws_region_name,
                                     aws_secret_access_key=self.__enviroments.aws_secret_access_key)

    def upload_file(self, file: bytes, key: str) -> None:
        self.__s3.put_object(Bucket=self.__enviroments.s3_bucket_name, Body=file, Key=key)
