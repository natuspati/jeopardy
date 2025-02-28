from typing import Annotated

from pydantic import BeforeValidator

from jlib.enums.prompt import QuestionTypeEnum, AnswerTypeEnum
from jlib.schemas.base import BaseSchema
from jlib.types.prompt import QuestionShowType, AnswerShowType


def _convert_question_type_to_str(question_type: int | str | QuestionTypeEnum) -> str:
    if isinstance(question_type, QuestionTypeEnum):
        return question_type.name.lower()

    try:
        return QuestionTypeEnum(question_type).name.lower()
    except ValueError:
        try:
            return QuestionTypeEnum[question_type].name.lower()
        except KeyError:
            raise ValueError(f"Invalid question type: {question_type}")


def _convert_str_to_question_type(question_type: str | int | QuestionTypeEnum) -> QuestionTypeEnum:
    if isinstance(question_type, QuestionTypeEnum):
        return question_type

    try:
        return QuestionTypeEnum(question_type)
    except ValueError:
        try:
            return QuestionTypeEnum[question_type.upper()]
        except KeyError:
            raise ValueError(f"Invalid question type: {question_type}")


def _convert_answer_type_to_str(answer_type: int | str | AnswerTypeEnum) -> str:
    if isinstance(answer_type, AnswerTypeEnum):
        return answer_type.name.lower()

    try:
        return AnswerTypeEnum(answer_type).name.lower()
    except ValueError:
        try:
            return AnswerTypeEnum[answer_type].name.lower()
        except KeyError:
            raise ValueError(f"Invalid question type: {answer_type}")


def _convert_str_to_answer_type(answer_type: str | int | AnswerTypeEnum) -> AnswerTypeEnum:
    if isinstance(answer_type, AnswerTypeEnum):
        return answer_type

    try:
        return AnswerTypeEnum(answer_type)
    except ValueError:
        try:
            return AnswerTypeEnum[answer_type.upper()]
        except KeyError:
            raise ValueError(f"Invalid question type: {answer_type}")


class PromptSchema(BaseSchema):
    id: int
    question: str
    question_type: QuestionTypeEnum
    answer: str
    answer_type: AnswerTypeEnum
    default_priority: int
    category_id: int


class PromptCreateShowSchema(BaseSchema):
    question: str
    question_type: QuestionShowType
    answer: str
    answer_type: AnswerShowType
    default_priority: int


class PromptCreateSchema(BaseSchema):
    question: str
    question_type: Annotated[
        QuestionTypeEnum, BeforeValidator(_convert_str_to_question_type)
    ]
    answer: str
    answer_type: Annotated[
        QuestionTypeEnum, BeforeValidator(_convert_str_to_answer_type)
    ]
    default_priority: int
    category_id: int


class PromptShowSchema(BaseSchema):
    id: int
    question: str
    question_type: Annotated[
        QuestionShowType, BeforeValidator(_convert_question_type_to_str)
    ]
    answer: str
    answer_type: Annotated[
        AnswerShowType, BeforeValidator(_convert_answer_type_to_str)
    ]
    default_priority: int
    category_id: int


class PromptPriorityUpdateSchema(BaseSchema):
    id: int
    default_priority: int
