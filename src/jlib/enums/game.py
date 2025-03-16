from enum import Enum


class LobbyMemberTypeEnum(Enum):
    LEAD = "lead"
    PLAYER = "player"


class LobbyStateEnum(Enum):
    CREATED = "created"
    INITIATED = "initiated"
    SELECT_QUESTION = "select_question"
    ANSWER_QUESTION_SELECTED = "answer_question_selected"
    ANSWER_QUESTION_ALL = "answer_question_all"
    RATE_ANSWER = "rate_answer"
    SHOW_ANSWER = "show_answer"
    FINISHED = "finished"
