import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from jlib.db import DBManager
from jlib.utils.auth import hash_password
from models.user import UserModel


@pytest.fixture
async def users(users_data: list[dict], db_manager: DBManager) -> list[UserModel]:
    user_models = [UserModel(**u) for u in users_data]
    for user_model in user_models:
        user_model.password = hash_password(user_model.password)
    async with db_manager.session() as session:
        session: AsyncSession
        session.add_all(user_models)
        await session.commit()
    return user_models
