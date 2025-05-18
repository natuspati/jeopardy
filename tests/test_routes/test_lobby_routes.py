import json
from collections.abc import Callable

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fixtures.factory_fixtures import LobbyFactory
from redis.asyncio import Redis

from jlib.enums import LobbyMemberTypeEnum, LobbyStateEnum
from jlib.schemas.lobby import LobbySchema
from models.preset import PresetModel
from models.user import UserModel
from settings import settings


async def test_get_lobbies(
    client: TestClient,
    redis_client: Redis,
    pagination: dict[str, int],
    lobby_factory: LobbyFactory,
):
    lobby_count = 5
    lobbies = lobby_factory.batch(size=lobby_count)
    for lobby in lobbies:
        await redis_client.set(
            name=f"{settings.redis_namespace}lobby_lobby_id={lobby.id}",
            value=lobby.model_dump_json(),
        )
    resp = client.get("/api/v1/lobby", params=pagination)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["items"]) == lobby_count


async def test_create_lobby(
    client: TestClient,
    redis_client: Redis,
    presets: list[PresetModel],
    user: UserModel,
    auth_header: Callable[[UserModel], dict[str, str]],
):
    selected_preset = next((p for p in presets if p.owner_id == user.id), None)
    if not selected_preset:
        pytest.fail("No preset found")

    resp = client.post(
        "/api/v1/lobby",
        json={"preset_id": 1},
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_201_CREATED
    created_lobby = resp.json()
    lobby_id = created_lobby.get("id")
    assert created_lobby.get("state") == LobbyStateEnum.CREATE.value
    assert lobby_id in created_lobby.get("join_url")

    stored_lobby = await redis_client.get(
        f"{settings.redis_namespace}lobby_lobby_id={lobby_id}",
    )
    stored_lobby = json.loads(stored_lobby)
    assert created_lobby["num_players"] == len(stored_lobby["players"])
    assert len(stored_lobby["categories"]) == len(selected_preset.categories)


async def test_join_lobby(
    client: TestClient,
    users: list[UserModel],
    auth_query_param: Callable[[UserModel], dict[str, str]],
    lobby: LobbySchema,
):
    player = next(
        (p for p in lobby.players if p.type == LobbyMemberTypeEnum.PLAYER),
        None,
    )
    if not player:
        pytest.fail("No player in lobby")
    user = next(u for u in users if u.id == player.user_id)

    with client.websocket_connect(
        f"/api/v1/lobby/{player.lobby_id}/join",
        params=auth_query_param(user),
    ) as websocket:
        data = websocket.receive_json()
    assert data.get("meta")
    assert player.username in data["meta"]
