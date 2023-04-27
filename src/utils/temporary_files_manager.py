from string import ascii_letters
from random import sample
from os import mkdir
from os.path import exists
from shutil import rmtree


class TemporaryFilesManager:

    def __init__(self, dir_path: str) -> None:
        if not exists(dir_path):
            mkdir(dir_path)

        self.__dir_path: str = dir_path

    def __assign_file_name(self) -> str:
        return ''.join(sample(ascii_letters, k=8))

    def write_data(self, data, is_binary: bool = False) -> str:
        mode: str = 'wb' if is_binary else 'w'

        file_name: str = self.__assign_file_name()

        with open(f'{self.__dir_path}/{file_name}', mode) as temp_file:
            temp_file.write(data)

        return f'{self.__dir_path}/{file_name}'

    def get_video_bytes(self, file_name: str) -> bytes:
        with open(file_name, 'rb') as video:
            return video.read()

    def __del__(self):
        try:
            rmtree(self.__dir_path)
        except:
            pass
