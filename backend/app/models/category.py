from __future__ import annotations
from typing import Optional, List

from pydantic import Field

from app.models.core import IDModelMixin, CoreModel


class CategoryBase(CoreModel):
    """
    All common characteristics of Category resource
    """
    
    name: Optional[str]


class CategoryCreate(CategoryBase):
    name: str = Field(min_length=1)
    questions: Optional[List[QuestionCreate]] = None


class CategoryUpdate(CategoryBase):
    name: str = Field(min_length=1)


class CategoryInDB(IDModelMixin, CategoryBase):
    name: str


class CategoryPublic(CategoryInDB):
    questions: List[QuestionPublic] = []


from app.models.question import QuestionPublic, QuestionCreate  # noqa E402

CategoryPublic.model_rebuild()
CategoryCreate.model_rebuild()
