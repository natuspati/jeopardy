from typing import Annotated

from pydantic import BeforeValidator, Field

from jlib.enums.prompt import AnswerTypeEnum, QuestionTypeEnum
from jlib.schemas.base import BaseSchema, OneFieldSetSchemaMixin
from jlib.types.prompt import AnswerShowType, QuestionShowType


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


def _convert_str_to_question_type(
    question_type: str | int | QuestionTypeEnum | None,
) -> int:
    if isinstance(question_type, QuestionTypeEnum):
        return question_type.value
    try:
        return QuestionTypeEnum[question_type.upper()].value
    except KeyError:
        try:
            return QuestionTypeEnum(question_type).value
        except ValueError:
            return question_type


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


def _convert_str_to_answer_type(
    answer_type: str | int | AnswerTypeEnum | None,
) -> int:
    if isinstance(answer_type, AnswerTypeEnum):
        return answer_type.value
    try:
        return AnswerTypeEnum[answer_type.upper()].value
    except KeyError:
        try:
            return AnswerTypeEnum(answer_type).value
        except ValueError:
            return answer_type


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
    answer_type: Annotated[AnswerShowType, BeforeValidator(_convert_answer_type_to_str)]
    default_priority: int
    category_id: int


class PromptPriorityUpdateSchema(BaseSchema):
    id: int = Field(serialization_alias="prompt_id")
    default_priority: int


class PromptUpdateShowSchema(BaseSchema, OneFieldSetSchemaMixin):
    question: str | None = None
    question_type: QuestionShowType | None = None
    answer: str | None = None
    answer_type: AnswerShowType | None = None


class PromptUpdateSchema(BaseSchema):
    id: int
    category_id: int
    question: str | None = None
    question_type: Annotated[
        QuestionTypeEnum | None, BeforeValidator(_convert_str_to_question_type)
    ] = None
    answer: str | None = None
    answer_type: Annotated[
        QuestionTypeEnum | None, BeforeValidator(_convert_str_to_answer_type)
    ] = None
