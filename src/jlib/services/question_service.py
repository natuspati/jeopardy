from abc import ABC, abstractmethod

from jlib.schemas.category import (
    BasicCategorySchema,
    CategoryCreateSchema,
    CategorySchema, CategoryFullUpdateSchema,
)
from jlib.schemas.prompt import PromptCreateSchema, PromptSchema


class BaseQuestionService(ABC):
    @abstractmethod
    async def get_category_by_id(self, category_id: int) -> CategorySchema | None:
        pass

    @abstractmethod
    async def get_category_by_name(self, category_name: str) -> CategorySchema | None:
        pass

    @abstractmethod
    async def get_categories(self, **kwargs) -> list[BasicCategorySchema]:
        pass

    @abstractmethod
    async def create_category(
        self,
        category_create: CategoryCreateSchema,
    ) -> BasicCategorySchema:
        pass

    @abstractmethod
    async def update_category(self, category_update: CategoryFullUpdateSchema) -> CategorySchema:
        pass

    @abstractmethod
    async def delete_category(self, category_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def create_prompt(self, prompt_create: PromptCreateSchema) -> PromptSchema:
        pass
