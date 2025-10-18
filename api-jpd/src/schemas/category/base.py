from pydantic import BaseModel, Field


class BaseCategorySchema(BaseModel):
    id: int
    name: str
    owner_id: int


class CategoryCreatePublicSchema(BaseModel):
    name: str = Field(min_length=3, max_length=64)


class CategoryCreateSchema(CategoryCreatePublicSchema):
    owner_id: int
