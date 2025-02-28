from abc import ABC, abstractmethod

from jlib.schemas.user import UserCreateSchema, UserUpdateSchema


class BaseUserDAL(ABC):
    @abstractmethod
    async def select_by_id(self, user_id: int, allow_deleted: bool):
        pass

    @abstractmethod
    async def select_by_username(self, username: str):
        pass

    @abstractmethod
    async def create(self, user_create: UserCreateSchema):
        pass

    @abstractmethod
    async def update_by_id(self, user_id: int, user_update: UserUpdateSchema):
        pass

    @abstractmethod
    async def delete(self, user_id: int):
        pass
