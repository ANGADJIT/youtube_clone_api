import boto3
from utils.config import Enviroments
import socket


class AWSManager:

    def __init__(self) -> None:
        self.__enviroments = Enviroments()

        # aws cred init
        if self.__enviroments.server_type == 'DEV':
            hostname: str = socket.gethostname()
            host: str = socket.gethostbyname(hostname)

            self.__s3 = boto3.client('s3',
                                     endpoint_url=f'http://{host}:9000',
                                     region_name='us-east-1',
                                     aws_access_key_id=self.__enviroments.aws_access_key_id,
                                     aws_secret_access_key=self.__enviroments.aws_secret_access_key)

        else:
            self.__s3 = boto3.client('s3',
                                     aws_access_key_id=self.__enviroments.aws_access_key_id,
                                     region_name=self.__enviroments.aws_region_name,
                                     aws_secret_access_key=self.__enviroments.aws_secret_access_key)

    def upload_file(self, file: bytes, key: str) -> None:
        self.__s3.put_object(
            Bucket=self.__enviroments.s3_bucket_name, Body=file, Key=key)

    def generate_link(self, object_name: str, for_video: bool) -> str:
        url: str = self.__s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.__enviroments.s3_bucket_name,
                    'Key': object_name,
                    'ResponseContentType': 'video/mp4' if for_video else 'image/*'},
            ExpiresIn=3600,
            HttpMethod='GET',
        )

        return url
