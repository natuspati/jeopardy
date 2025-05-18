from typing import Annotated

from pydantic import AfterValidator, Field

from jlib.schemas.base import BaseSchema, OneFieldSetSchemaMixin
from jlib.schemas.pagination import PaginatedResponseSchema
from jlib.schemas.prompt import (
    PromptInGameSchema,
    PromptPriorityUpdateSchema,
    PromptSchema,
    PromptShowSchema,
)


def _sort_prompts_by_priority(
    prompts: list[PromptShowSchema | PromptPriorityUpdateSchema],
) -> list[PromptShowSchema]:
    seen = set()
    for p in prompts:
        if p.default_priority in seen:
            raise ValueError("Prompts must have unique priorities")
        seen.add(p.default_priority)
    prompts.sort(key=lambda p: p.default_priority)
    return prompts


class CategorySchema(BaseSchema):
    id: int
    name: str
    owner_id: int
    prompts: list[PromptSchema] = Field(default_factory=list)


class BasicCategorySchema(BaseSchema):
    id: int
    name: str
    owner_id: int


class CategoryShowSchema(BaseSchema):
    id: int
    name: str
    prompts: Annotated[
        list[PromptShowSchema],
        AfterValidator(_sort_prompts_by_priority),
    ] = Field(default_factory=list)


class BasicCategoryShowSchema(BaseSchema):
    id: int
    name: str


class CategoryCreateSchema(BaseSchema):
    name: str
    owner_id: int


class CategoryCreateShowSchema(BaseSchema):
    name: str


class CategoryPartialUpdateSchema(BaseSchema):
    id: int
    name: str


class CategoryUpdateShowSchema(BaseSchema, OneFieldSetSchemaMixin):
    name: str | None = None
    prompts: Annotated[
        list[PromptPriorityUpdateSchema],
        AfterValidator(_sort_prompts_by_priority),
    ] = Field(default_factory=list)


class CategoryFullUpdateSchema(BaseSchema):
    id: int
    name: str | None = None
    owner_id: int
    prompts: Annotated[
        list[PromptPriorityUpdateSchema],
        AfterValidator(_sort_prompts_by_priority),
    ] = Field(default_factory=list)


class PromptCategorySchema(PromptSchema):
    category: BasicCategorySchema


class PaginatedBasicCategorySchema(PaginatedResponseSchema[BasicCategorySchema]):
    pass


class PaginatedBasicCategoryShowSchema(
    PaginatedResponseSchema[BasicCategoryShowSchema],
):
    pass


class CategoryInGameSchema(BaseSchema):
    id: int
    name: str
    prompts: Annotated[
        list[PromptInGameSchema],
        AfterValidator(_sort_prompts_by_priority),
    ] = Field(default_factory=list)
