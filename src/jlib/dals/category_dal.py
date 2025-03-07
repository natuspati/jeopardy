from abc import ABC, abstractmethod

from jlib.schemas.category import CategoryCreateSchema, CategoryPartialUpdateSchema


class BaseCategoryDAL(ABC):
    @abstractmethod
    async def select_by_id(self, category_id: int):
        pass

    @abstractmethod
    async def select_by_name(self, category_name: str):
        pass

    @abstractmethod
    async def select(self, *, offset: int, limit: int):
        pass

    @abstractmethod
    async def create(self, category: CategoryCreateSchema):
        pass

    @abstractmethod
    async def update(self, category_id: int, category: CategoryPartialUpdateSchema):
        pass

    @abstractmethod
    async def delete(self, category_id: int):
        pass
