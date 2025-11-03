from typing import Annotated

from fastapi import Depends

from auth.password import hash_password
from errors.request import BadRequestError
from repositories import UserRepo
from schemas.user.base import BaseUserSchema, UserCreatePublicSchema, UserCreateSchema
from schemas.user.nested import UserSchema


class UserService:
    def __init__(self, user_repo: Annotated[UserRepo, Depends()]):
        self._user_repo = user_repo

    async def get_user(
        self,
        user_id: int | None = None,
        username: str | None = None,
        extra: bool = True,
    ) -> UserSchema | BaseUserSchema | None:
        if user_id is None and username is None:
            raise BadRequestError("User ID or username are required")
        return await self._user_repo.select(
            user_id=user_id,
            username=username,
            load_lobbies=extra,
            load_categories=extra,
        )

    async def get_users(
        self,
        *user_ids: int,
        extra: bool = False,
    ) -> list[UserSchema] | list[BaseUserSchema]:
        if not user_ids:
            return []

        return await self._user_repo.select_many(
            *user_ids,
            load_lobbies=extra,
            load_categories=extra,
        )

    async def create_user(self, user: UserCreatePublicSchema) -> BaseUserSchema:
        user_with_hash_pass = UserCreateSchema(
            username=user.username,
            password=hash_password(user.password),
        )
        return await self._user_repo.insert(user_with_hash_pass)
