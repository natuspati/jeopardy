from pydantic import BaseModel, Field

from schemas.base import OneFieldSetMixin


class BaseCategorySchema(BaseModel):
    id: int
    name: str
    owner_id: int


class CategoryCreatePublicSchema(BaseModel):
    name: str = Field(min_length=3, max_length=64)


class CategoryCreateSchema(CategoryCreatePublicSchema):
    owner_id: int


class CategorySearchSchema(BaseModel, OneFieldSetMixin):
    name: str | None = Field(default=None, min_length=2, max_length=64)
    is_valid: bool | None = None
    owner_id: int | None = None
