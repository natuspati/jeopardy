from enum import StrEnum, auto


class LobbyStateEnum(StrEnum):
    CREATED = auto()
    STARTED = auto()
    FINISHED = auto()
