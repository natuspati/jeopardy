from typing import Callable

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jlib.db import DBManager
from models.preset import PresetModel
from models.preset_category import PresetCategoryModel
from models.prompt import PromptModel
from models.user import UserModel


def test_get_presets(
    client: TestClient,
    pagination: dict[str, int],
    user: UserModel,
    presets: list[PresetModel],
    token_generator: Callable[[UserModel], dict[str, str]],
):
    selected_presets = [p for p in presets if p.owner_id == user.id]
    if not user:
        pytest.fail("No user found")
    resp = client.get(
        "/api/v1/preset",
        params={
            "offset": pagination["offset"],
            "limit": pagination["limit"],
        },
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_200_OK
    fetched_presets = resp.json()["items"]
    assert len(fetched_presets) == len(selected_presets)
    for fetched_preset in fetched_presets:
        selected_preset = next(
            (p for p in selected_presets if p.id == fetched_preset.pop("id")), None
        )
        assert selected_preset
        for field, value in fetched_preset.items():
            assert value == getattr(selected_preset, field)


def test_get_preset(
    client: TestClient,
    users: list[UserModel],
    prompts: list[PromptModel],
    presets: list[PresetModel],
    token_generator: Callable[[UserModel], dict[str, str]],
):
    user, wrong_user = users[0], users[1]
    preset = next((p for p in presets if p.owner_id == user.id), None)
    if not preset:
        pytest.fail("No preset for provided user")

    # success
    resp = client.get(
        f"/api/v1/preset/{preset.id}",
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_200_OK
    fetched_preset = resp.json()
    fetched_categories = fetched_preset.pop("categories")
    for field, value in fetched_preset.items():
        assert value == getattr(preset, field)
    preset_category_ids = set(cat.id for cat in preset.categories)
    category_prompts = {
        cat_id: {p.id for p in prompts if p.category_id == cat_id}
        for cat_id in preset_category_ids
    }
    for category in fetched_categories:
        cat_id = category.pop("id")
        assert cat_id in preset_category_ids
        for prompt in category.pop("prompts"):
            assert prompt["id"] in category_prompts[cat_id]

    # user does not own preset
    resp = client.get(
        f"/api/v1/preset/{preset.id}",
        headers=token_generator(wrong_user),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # preset does not exist
    non_existent_preset_id = max((p.id for p in presets)) + 1
    resp = client.get(
        f"/api/v1/preset/{non_existent_preset_id}",
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_create_preset(
    client: TestClient,
    user: UserModel,
    token_generator: Callable[[UserModel], dict[str, str]],
    db_manager: DBManager,
):
    # success with provided name
    new_preset = "new preset"
    resp = client.post(
        "/api/v1/preset",
        json={"name": new_preset},
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_201_CREATED
    async with db_manager.session() as session:
        created_preset = await session.get(PresetModel, resp.json()["id"])
    assert created_preset
    assert created_preset.name == new_preset
    assert created_preset.owner_id == user.id

    # success without provided name
    resp = client.post(
        "/api/v1/preset",
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_201_CREATED
    async with db_manager.session() as session:
        created_preset = await session.get(PresetModel, resp.json()["id"])
    assert created_preset
    assert created_preset.name


def test_update_preset(
    client: TestClient,
    users: list[UserModel],
    presets: list[PresetModel],
    token_generator: Callable[[UserModel], dict[str, str]],
):
    user, wrong_user = users[0], users[1]
    preset = next((p for p in presets if p.owner_id == user.id), None)
    if not preset:
        pytest.fail("No preset to delete with provided user")

    # success
    new_preset = "new preset"
    new_categories = {cat.id for cat in preset.categories[1:]}
    resp = client.patch(
        f"/api/v1/preset/{preset.id}",
        json={"name": new_preset, "categories": list(new_categories)},
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_200_OK
    fetched_preset: dict = resp.json()
    assert fetched_preset["name"] == new_preset
    assert {cat["id"] for cat in fetched_preset["categories"]} == new_categories

    # user does not own preset
    resp = client.patch(
        f"/api/v1/preset/{preset.id}",
        json={"name": new_preset, "categories": list(new_categories)},
        headers=token_generator(wrong_user),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # wrong preset
    non_existent_preset_id = max((p.id for p in presets)) + 1
    resp = client.patch(
        f"/api/v1/preset/{non_existent_preset_id}",
        json={"name": new_preset, "categories": list(new_categories)},
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # invalid input
    resp = client.patch(
        f"/api/v1/preset/{preset.id}",
        json={"categories": 1},
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    resp = client.patch(
        f"/api/v1/preset/{preset.id}",
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_delete_preset(
    client: TestClient,
    users: list[UserModel],
    presets: list[PresetModel],
    token_generator: Callable[[UserModel], dict[str, str]],
    db_manager: DBManager,
):
    user, wrong_user = users[0], users[1]
    preset = next((p for p in presets if p.owner_id == user.id), None)
    if not preset:
        pytest.fail("No preset to delete with provided user")

    # user does not own preset
    resp = client.delete(
        f"/api/v1/preset/{preset.id}",
        headers=token_generator(wrong_user),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # preset does not exist
    non_existent_preset_id = max((p.id for p in presets)) + 1
    resp = client.delete(
        f"/api/v1/preset/{non_existent_preset_id}",
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # success
    resp = client.delete(
        f"/api/v1/preset/{preset.id}",
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    async with db_manager.session() as session:
        session: AsyncSession
        deleted_preset = await session.get(PresetModel, preset.id)
        assert not deleted_preset

        preset_categories = await session.scalars(
            select(PresetCategoryModel).where(
                PresetCategoryModel.preset_id == preset.id
            )
        )
        assert not preset_categories.all()
