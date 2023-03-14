from string import ascii_letters
from random import sample


class __RawVideosManager:

    def __init__(self) -> None:
        self.__raw_videos: dict[str, bytes] = {}

    def add_video(self, video: bytes) -> str:
        key: str = ''.join(sample(ascii_letters, k=8))

        self.__raw_videos[key] = video

        return key

    def get_video(self, key: str) -> bytes | None:
        return self.__raw_videos.get(key)


raw_videos_manager: __RawVideosManager = __RawVideosManager()
