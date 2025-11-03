from enum import StrEnum, auto


class PlayerStateEnum(StrEnum):
    SELECTED = auto()
    CONNECTED = auto()
    DISCONNECTED = auto()
    BANNED = auto()


class LeadStateEnum(StrEnum):
    CONNECTED = auto()
    DISCONNECTED = auto()
