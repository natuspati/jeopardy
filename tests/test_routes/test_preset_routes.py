from typing import Callable

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from models.preset import PresetModel
from models.user import UserModel


def test_get_presets(
    client: TestClient,
    pagination: dict[str, int],
    users: list[UserModel],
    presets: list[PresetModel],
    token_generator: Callable[[UserModel], dict[str, str]],
):
    user = users[0]
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
