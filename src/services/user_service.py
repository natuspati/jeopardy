from typing import Annotated

from fastapi import Depends

from dals import UserDAL
from jlib.errors.resource import ResourceExistsError
from jlib.schemas.user import UserCreateSchema, UserSchema
from jlib.services import BaseUserService, SchemaValidationServiceMixin
from jlib.utils.auth import hash_password


class UserService(BaseUserService, SchemaValidationServiceMixin):
    def __init__(self, user_dal: Annotated[UserDAL, Depends()]):
        super().__init__(user_dal)

    async def get_by_id(
        self,
        user_id: int,
        allow_deleted: bool = False,
    ) -> UserSchema | None:
        user_in_db = await self._dal.select_by_id(user_id, allow_deleted)
        if user_in_db:
            return self._validate(user_in_db, UserSchema)

    async def get_by_username(
        self,
        username: str,
        allow_deleted: bool = False,
    ) -> UserSchema | None:
        user_in_db = await self._dal.select_by_username(username)
        if user_in_db:
            return self._validate(user_in_db, UserSchema)

    async def register(self, user_create: UserCreateSchema) -> UserSchema:
        existing_user = await self.get_by_username(user_create.username)
        if existing_user:
            raise ResourceExistsError(existing_user.username)

        user_create.password = self._hash_password(user_create.password)
        user_in_db = await self._dal.create(user_create)
        return self._validate(user_in_db, UserSchema)

    async def delete(self, user_id: int) -> None:
        await self._dal.delete(user_id)

    @classmethod
    def _hash_password(cls, password: str) -> str:
        return hash_password(password)
