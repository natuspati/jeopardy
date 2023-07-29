from typing import Optional, Union

from pydantic import PositiveInt

from app.models.core import IDModelMixin, CoreModel
from app.models.category import CategoryPublic, CategoryInDB


class QuestionBase(CoreModel):
    """
    All common characteristics of Question resource
    """
    question: Optional[str]
    answer: Optional[bool]
    value: Optional[PositiveInt]


class QuestionCreate(QuestionBase):
    question: str
    answer: str
    value: PositiveInt


class QuestionUpdate(QuestionBase):
    pass


class QuestionInDB(IDModelMixin, QuestionBase):
    category_id: str
    question: str
    answer: str
    value: PositiveInt


class QuestionPublic(QuestionInDB):
    pass
