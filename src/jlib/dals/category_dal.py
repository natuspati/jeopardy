from abc import ABC, abstractmethod

from jlib.schemas.category import (
    BasicCategorySchema,
    CategoryCreateSchema,
    CategoryPartialUpdateSchema,
    CategorySchema,
)


class BaseCategoryDAL(ABC):
    @abstractmethod
    async def select_by_id(self, category_id: int) -> CategorySchema | None:
        pass

    @abstractmethod
    async def select_by_name(self, category_name: str) -> CategorySchema | None:
        pass

    @abstractmethod
    async def select(self, *, offset: int, limit: int) -> list[BasicCategorySchema]:
        pass

    @abstractmethod
    async def create(self, category: CategoryCreateSchema) -> BasicCategorySchema:
        pass

    @abstractmethod
    async def update(
        self,
        category_id: int,
        category: CategoryPartialUpdateSchema,
    ) -> None:
        pass

    @abstractmethod
    async def delete(self, category_id: int) -> None:
        pass
