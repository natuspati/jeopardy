from sqlalchemy import select, update

from jlib.dals import BaseUserDAL, RelationalDAL
from jlib.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from jlib.utils.validation import validate_model
from models.user import UserModel


class UserDAL(BaseUserDAL, RelationalDAL):
    async def select_by_id(
        self,
        user_id: int,
        allow_deleted: bool = False,
    ) -> UserSchema | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        if allow_deleted:
            stmt = stmt.where(UserModel.deleted.is_(False))
        user = await self.scalar(stmt)
        return validate_model(user, UserSchema)

    async def select_by_username(self, username: str) -> UserSchema | None:
        stmt = select(UserModel).where(UserModel.username == username)
        user = await self.scalar(stmt)
        return validate_model(user, UserSchema)

    async def create(self, user_create: UserCreateSchema) -> UserSchema:
        user = UserModel(deleted=False, **user_create.model_dump())
        async with self.session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return validate_model(user, UserSchema)

    async def update_by_id(
        self,
        user_id: int,
        user_update: UserUpdateSchema,
    ) -> UserSchema:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(user_update.model_dump(exclude_unset=True))
        )
        await self.execute(stmt)
        return await self.select_by_id(user_id)

    async def delete(self, user_id: int) -> None:
        stmt = update(UserModel).where(UserModel.id == user_id).values(deleted=True)
        return await self.execute(stmt)
