from abc import ABC, abstractmethod

from jlib.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema


class BaseUserDAL(ABC):
    @abstractmethod
    async def select_by_id(
        self,
        user_id: int,
        allow_deleted: bool,
    ) -> UserSchema | None:
        pass

    @abstractmethod
    async def select_by_username(self, username: str) -> UserSchema | None:
        pass

    @abstractmethod
    async def create(self, user_create: UserCreateSchema) -> UserSchema:
        pass

    @abstractmethod
    async def update_by_id(
        self, user_id: int, user_update: UserUpdateSchema
    ) -> UserSchema:
        pass

    @abstractmethod
    async def delete(self, user_id: int):
        pass
