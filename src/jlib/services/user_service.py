from abc import ABC, abstractmethod

from jlib.schemas.user import UserCreateSchema, UserSchema


class BaseUserService(ABC):
    @abstractmethod
    async def get_by_id(
        self,
        user_id: int,
        allow_deleted: bool = False,
    ) -> UserSchema | None:
        pass

    @abstractmethod
    async def get_by_username(
        self,
        username: str,
        allow_deleted: bool = False,
    ) -> UserSchema | None:
        pass

    @abstractmethod
    async def register(self, user_create: UserCreateSchema) -> UserSchema:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass
