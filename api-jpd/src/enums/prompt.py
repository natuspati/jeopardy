from enum import StrEnum, auto


class PromptTypeEnum(StrEnum):
    TEXT = auto()
    IMAGE = auto()
    VIDEO = auto()


class PromptStateEnum(StrEnum):
    SELECTED = auto()
    NOT_SELECTED = auto()
