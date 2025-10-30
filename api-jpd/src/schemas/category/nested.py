from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from constants import NUM_PROMPTS_IN_CATEGORY
from schemas.base import OneFieldSetMixin, supplied_value_is_not_none
from schemas.category.base import BaseCategorySchema
from schemas.lobby.base import BaseLobbySchema
from schemas.lobby_category.base import BaseLobbyCategorySchema
from schemas.prompt.base import BasePromptSchema, PromptInGameSchema, PromptOrderUpdateSchema
from schemas.user.base import BaseUserSchema


class CategorySchema(BaseCategorySchema):
    owner: BaseUserSchema
    prompts: list[BasePromptSchema]
    lobbies: list[BaseLobbySchema]
    lobby_categories: list[BaseLobbyCategorySchema]

    @property
    def is_full(self) -> bool:
        return len(self.prompts) >= NUM_PROMPTS_IN_CATEGORY

    @property
    def is_valid(self) -> bool:
        return self.is_full and sorted([p.order for p in self.prompts]) == list(
            range(1, NUM_PROMPTS_IN_CATEGORY + 1),
        )


class CategoryWithPromptsSchema(BaseCategorySchema):
    prompts: list[BasePromptSchema]


class CategoryUpdateSchema(BaseModel, OneFieldSetMixin):
    name: str | None = Field(default=None, min_length=3, max_length=64)
    prompts: list[PromptOrderUpdateSchema] | None = None

    @field_validator("name")
    @classmethod
    def check_supplied_values_not_none(
        cls,
        value: int | list[int] | None,
        info: ValidationInfo,
    ) -> int | list[int]:
        return supplied_value_is_not_none(value, info)

    @field_validator("prompts")
    @classmethod
    def validate_prompt_orders(
        cls,
        prompts: list[PromptOrderUpdateSchema] | None,
        info: ValidationInfo,
    ) -> list[PromptOrderUpdateSchema] | None:
        supplied_value_is_not_none(prompts, info)

        orders = [p.order for p in prompts]

        if len(orders) != len(set(orders)):
            raise ValueError("Prompt orders must be unique.")

        sorted_orders = sorted(orders)
        expected = list(range(1, len(sorted_orders) + 1))
        if sorted_orders != expected:
            raise ValueError(
                f"Prompt orders must start at 1 and be continuous (expected {expected}).",
            )

        if len(orders) > NUM_PROMPTS_IN_CATEGORY:
            raise ValueError(f"A category cannot have more than {NUM_PROMPTS_IN_CATEGORY} prompts.")

        return prompts


class CategoryInGameSchema(BaseModel):
    id: int
    name: str
    prompts: list[PromptInGameSchema]
