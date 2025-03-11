from abc import ABC, abstractmethod

from jlib.schemas.category import (
    BasicCategorySchema,
    CategoryCreateSchema,
    CategoryFullUpdateSchema,
    CategorySchema,
    PaginatedBasicCategorySchema,
)
from jlib.schemas.prompt import PromptCreateSchema, PromptSchema, PromptUpdateSchema


class BaseQuestionService(ABC):
    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> CategorySchema | None:
        pass

    @abstractmethod
    async def get_category_by_name(self, category_name: str) -> CategorySchema | None:
        pass

    @abstractmethod
    async def get_categories(self, **kwargs) -> PaginatedBasicCategorySchema:
        pass

    @abstractmethod
    async def create_category(
        self,
        category_create: CategoryCreateSchema,
    ) -> BasicCategorySchema:
        pass

    @abstractmethod
    async def update_category(
        self,
        category_update: CategoryFullUpdateSchema,
    ) -> CategorySchema:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def create_prompt(
        self,
        user_id: int,
        prompt_create: PromptCreateSchema,
    ) -> PromptSchema:
        pass

    @abstractmethod
    async def update_prompt(
        self, user_id: int, prompt_update: PromptUpdateSchema
    ) -> PromptSchema:
        pass
