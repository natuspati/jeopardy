from sqlalchemy import insert, select, update

from jlib.dals.relational_dal import RelationalDAL
from jlib.dals.user_dal import BaseUserDAL
from jlib.schemas.user import UserCreateSchema, UserUpdateSchema
from models.user import UserModel


class UserDAL(BaseUserDAL, RelationalDAL):
    async def select_by_id(
        self, user_id: int, allow_deleted: bool = False
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        if allow_deleted:
            stmt = stmt.where(UserModel.deleted.is_(False))
        return await self.scalar(stmt)

    async def select_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.username == username)
        return await self.scalar(stmt)

    async def create(self, user_create: UserCreateSchema) -> UserModel:
        stmt = insert(UserModel).values(user_create.model_dump()).returning()
        return await self.scalar(stmt)

    async def update_by_id(
        self,
        user_id: int,
        user_update: UserUpdateSchema,
    ) -> UserModel:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(user_update.model_dump(exclude_unset=True))
        )
        return await self.scalar(stmt)

    async def delete(self, user_id: int) -> None:
        stmt = update(UserModel).where(UserModel.id == user_id).values(deleted=True)
        return await self.execute(stmt)
