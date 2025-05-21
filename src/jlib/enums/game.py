from enum import Enum


class LobbyMemberTypeEnum(Enum):
    LEAD = "lead"
    PLAYER = "player"


class BaseLobbyEnum(str, Enum):
    pass


class LobbyStateEnum(BaseLobbyEnum):
    CREATE = "create"
    START = "start"
    SELECT_PLAYER = "select_player"
    SELECT_QUESTION = "select_question"
    ANSWER_QUESTION_SELECTED = "answer_question_selected"
    ANSWER_QUESTION_ALL = "answer_question_all"
    RATE_ANSWER = "rate_answer"
    SHOW_ANSWER = "show_answer"
    FINISH = "finish"


class LobbyEventEnum(BaseLobbyEnum):
    JOIN = "join"
    ERROR = "error"
