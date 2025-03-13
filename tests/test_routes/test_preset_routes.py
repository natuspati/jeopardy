from typing import Callable

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jlib.db import DBManager
from models.preset import PresetModel
from models.preset_category import PresetCategoryModel
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
