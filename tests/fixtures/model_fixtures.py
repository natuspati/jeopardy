import pytest
from redis.asyncio import Redis
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from jlib.db import DBManager
from jlib.schemas.lobby import LobbySchema
from jlib.schemas.preset import PresetSchema
from jlib.utils.auth import hash_password
from jlib.utils.validation import validate_model
from models.category import CategoryModel
from models.preset import PresetModel
from models.preset_category import PresetCategoryModel
from models.prompt import PromptModel
from models.user import UserModel
from settings import settings


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
            select(PresetModel).options(
                selectinload(PresetModel.categories).selectinload(CategoryModel.prompts),
            ),
        )
    return res.all()


@pytest.fixture
async def lobby(
    users: list[UserModel],
    presets: list[PresetModel],
    lobby_data: dict,
    redis_client: Redis,
) -> LobbySchema:
    preset = validate_model(presets[0], PresetSchema)
    new_lobby = {
        "id": lobby_data["id"],
        "state": lobby_data["state"],
        "players": [
            {"user_id": next(u.id for u in users if u.username == p["username"]), **p}
            for p in lobby_data["players"]
        ],
        "categories": preset.model_dump()["categories"],
    }
    validated_lobby = validate_model(new_lobby, LobbySchema)
    await redis_client.set(
        name=f"{settings.redis_namespace}lobby_lobby_id={validated_lobby.id}",
        value=validated_lobby.model_dump_json(),
    )
    return validated_lobby
