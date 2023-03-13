from enum import Enum


class VideoType(Enum):

    MUSIC = 'MUSIC'
    DANCE = 'DANCE'
    COMEDY = 'COMEDY'
    INFORMATIONAL = 'INFORMATIONAL'
    EDUCATIONAL = 'EDUCATIONAL'
    HEALTH_CARE = 'HEALTH_CARE'

    def __str__(self) -> str:
        return self.value