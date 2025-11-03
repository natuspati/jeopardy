from enum import StrEnum, auto


class GameStateEnum(StrEnum):
    BEFORE_START = auto()
    SELECT_PLAYER = auto()
    SELECT_PROMPT = auto()
