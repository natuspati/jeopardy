from fastapi import status
from fastapi.testclient import TestClient
from fixtures.factory_fixtures import LobbyFactory
from redis.asyncio import Redis

from settings import settings


async def test_get_lobbies(
    client: TestClient,
    redis_client: Redis,
    lobby_factory: LobbyFactory,
):
    lobby_count = 5
    lobbies = lobby_factory.batch(size=lobby_count)
    for lobby in lobbies:
        await redis_client.set(
            name=f"{settings.redis_namespace}lobby_lobby_id={lobby.id}",
            value=lobby.model_dump_json(),
        )
    resp = client.get("/api/v1/lobby")
    assert resp.status_code == status.HTTP_200_OK
    fetched_lobbies = resp.json()
    assert len(fetched_lobbies) == lobby_count
    lobbies_in_db = [lobby.model_dump(mode="json") for lobby in lobbies]
    for fetched_lobby in fetched_lobbies:
        assert fetched_lobby in lobbies_in_db
