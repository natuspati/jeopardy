from typing import Annotated

from fastapi import Depends

from dals import UserDAL
from jlib.dals import BaseUserDAL
from jlib.errors.resource import ResourceExistsError
from jlib.schemas.user import UserCreateSchema, UserSchema
from jlib.services import BaseUserService
from jlib.utils.auth import hash_password


class UserService(BaseUserService):
    def __init__(self, user_dal: Annotated[BaseUserDAL, Depends(UserDAL)]):
        self._user_dal = user_dal

    async def get_by_id(
        self,
        user_id: int,
        allow_deleted: bool = False,
    ) -> UserSchema | None:
        return await self._user_dal.select_by_id(user_id, allow_deleted)

    async def get_by_username(
        self,
        username: str,
        allow_deleted: bool = False,
    ) -> UserSchema | None:
        return await self._user_dal.select_by_username(username)

    async def register(self, user_create: UserCreateSchema) -> UserSchema:
        existing_user = await self.get_by_username(user_create.username)
        if existing_user:
            raise ResourceExistsError(existing_user.username)
        user_create.password = self._hash_password(user_create.password)
        return await self._user_dal.create(user_create)

    async def delete(self, user_id: int) -> None:
        await self._user_dal.delete(user_id)

    @classmethod
    def _hash_password(cls, password: str) -> str:
        return hash_password(password)
