from typing import Annotated, Self

from pydantic import Field, AfterValidator, model_validator

from jlib.schemas.base import BaseSchema, OneFieldSetSchemaMixin
from jlib.schemas.prompt import (
    PromptSchema,
    PromptShowSchema,
    PromptPriorityUpdateSchema,
)


def _sort_prompts_by_priority(
    prompts: list[PromptShowSchema | PromptPriorityUpdateSchema],
) -> list[PromptShowSchema]:
    prompts.sort(key=lambda p: p.default_priority)
    return prompts


class CategorySchema(BaseSchema):
    id: int
    name: str
    owner_id: int
    prompts: list[PromptSchema] = Field(
        default_factory=list,
    )


class BasicCategorySchema(BaseSchema):
    id: int
    name: str
    owner_id: int


class CategoryShowSchema(BaseSchema):
    id: int
    name: str
    prompts: Annotated[
        list[PromptShowSchema], AfterValidator(_sort_prompts_by_priority)
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
        list[PromptPriorityUpdateSchema], AfterValidator(_sort_prompts_by_priority)
    ] = Field(default_factory=list)


class CategoryFullUpdateSchema(BaseSchema):
    id: int
    name: str | None = None
    prompts: Annotated[
        list[PromptPriorityUpdateSchema], AfterValidator(_sort_prompts_by_priority)
    ] = Field(default_factory=list)
