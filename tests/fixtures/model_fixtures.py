import pytest
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from jlib.db import DBManager
from jlib.utils.auth import hash_password
from models.category import CategoryModel
from models.preset import PresetModel
from models.preset_category import PresetCategoryModel
from models.prompt import PromptModel
from models.user import UserModel


@pytest.fixture
async def users(users_data: list[dict], db_manager: DBManager) -> list[UserModel]:
    user_models = [UserModel(**u) for u in users_data]
    for user_model in user_models:
        user_model.password = hash_password(user_model.password)
    async with db_manager.session() as session:
        session.add_all(user_models)
        await session.commit()
    return user_models


@pytest.fixture
async def user(users: list[UserModel]) -> UserModel:
    user = next((u for u in users if not u.deleted), None)
    if not user:
        pytest.fail("No user found")
    return user


@pytest.fixture
async def categories(
    categories_data: list[dict],
    users: list[UserModel],
    db_manager: DBManager,
) -> list[CategoryModel]:
    category_models = [CategoryModel(**cat) for cat in categories_data]
    async with db_manager.session() as session:
        session.add_all(category_models)
        await session.commit()
    return category_models


@pytest.fixture
async def prompts(
    prompts_data: list[dict],
    categories: list[CategoryModel],
    db_manager: DBManager,
) -> list:
    prompt_models = [PromptModel(**p) for p in prompts_data]
    async with db_manager.session() as session:
        session.add_all(prompt_models)
        await session.commit()
    return prompt_models


@pytest.fixture
async def presets(
    unpopulated_presets_data: list[dict],
    presets_data: list[dict],
    categories: list[CategoryModel],
    prompts: list[PromptModel],
    db_manager: DBManager,
) -> list[PresetModel]:
    async with db_manager.session() as session:
        await session.execute(insert(PresetModel).values(unpopulated_presets_data))
        await session.execute(insert(PresetCategoryModel).values(presets_data))
        res = await session.scalars(
            select(PresetModel).options(selectinload(PresetModel.categories))
        )
    return res.all()
