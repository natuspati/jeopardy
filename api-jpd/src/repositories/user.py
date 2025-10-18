from sqlalchemy import and_, insert, select
from sqlalchemy.orm import selectinload

from errors.request import BadRequestError
from models.user import UserModel
from repositories.mixins import RelationalRepoMixin
from schemas.user.base import BaseUserSchema, UserCreateSchema
from schemas.user.nested import UserSchema
from utils.validation import validate_model


class UserRepo(RelationalRepoMixin):
    async def select(
        self,
        *,
        user_id: int | None = None,
        username: str | None = None,
        load_categories: bool = True,
        load_lobbies: bool = True,
    ) -> UserSchema | BaseUserSchema | None:
        if user_id is None and username is None:
            raise BadRequestError("Either user ID or username must be provided")

        filters = []

        if user_id is not None:
            filters.append(UserModel.id == user_id)
        if username is not None:
            filters.append(UserModel.username == username)

        options = []
        if load_categories:
            options.append(selectinload(UserModel.categories))
        if load_lobbies:
            options.append(selectinload(UserModel.lobbies))

        stmt = select(UserModel).where(and_(*filters)).options(*options)
        user = await self.scalar(stmt)

        validation_schema = UserSchema if load_lobbies or load_categories else BaseUserSchema
        return validate_model(user, validation_schema)

    async def insert(self, user: UserCreateSchema) -> BaseUserSchema:
        stmt = insert(UserModel).values(user.model_dump()).returning(UserModel)
        created_user = await self.scalar(stmt)
        return validate_model(created_user, BaseUserSchema)
