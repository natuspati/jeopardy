from enum import StrEnum, auto


class PlayerStateEnum(StrEnum):
    ACTIVE = auto()
    DISCONNECTED = auto()
    BANNED = auto()
