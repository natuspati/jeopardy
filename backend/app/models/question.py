from typing import Optional

from pydantic import PositiveInt, Field

from app.models.core import IDModelMixin, CoreModel


class QuestionBase(CoreModel):
    """
    All common characteristics of Question resource
    """
    question: Optional[str]
    answer: Optional[str]
    value: Optional[PositiveInt]


class QuestionCreate(QuestionBase):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    value: PositiveInt


class QuestionUpdate(QuestionBase):
    question: Optional[str] = Field(default=None, min_length=1)
    answer: Optional[str] = Field(default=None, min_length=1)
    value: Optional[PositiveInt] = None


class QuestionInDB(IDModelMixin, QuestionBase):
    category_id: str
    question: str
    answer: str
    value: PositiveInt


class QuestionPublic(QuestionInDB):
    pass
