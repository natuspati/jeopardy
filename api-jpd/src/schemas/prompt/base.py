from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from constants import NUM_PROMPTS_IN_CATEGORY
from enums.prompt import PromptTypeEnum
from schemas.base import OneFieldSetMixin, supplied_value_is_not_none


class BasePromptSchema(BaseModel):
    id: int
    category_id: int
    question: str
    question_type: PromptTypeEnum
    answer: str
    answer_type: PromptTypeEnum
    order: int
    score: int


class PromptCreatePublicSchema(BaseModel):
    question: str
    question_type: PromptTypeEnum
    answer: str
    answer_type: PromptTypeEnum
    order: int
    score: int


class PromptCreateSchema(PromptCreatePublicSchema):
    category_id: int


class PromptUpdateSchema(BaseModel, OneFieldSetMixin):
    question: str | None = None
    question_type: PromptTypeEnum | None = None
    answer: str | None = None
    answer_type: PromptTypeEnum | None = None
    score: int | None = None

    @field_validator("question", "question_type", "answer", "answer_type", "score")
    @classmethod
    def check_supplied_values_not_none(
        cls,
        value: int | list[int] | None,
        info: ValidationInfo,
    ) -> int | list[int]:
        return supplied_value_is_not_none(value, info)


class PromptOrderUpdateSchema(BaseModel):
    id: int
    order: int = Field(ge=1, le=NUM_PROMPTS_IN_CATEGORY)
