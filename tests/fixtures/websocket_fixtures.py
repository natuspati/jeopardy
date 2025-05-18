import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest
from redis.asyncio import Redis

from dals import LobbyDAL
from jlib.redis import RedisManager
from jlib.schemas.lobby import LobbySchema
from jlib.ws import WSManager
from services.flow_service import GameFlowService


class MockWebSocket:
    def __init__(self):
        self._connected = False
        self._closed = False
        self.received = asyncio.Queue()
        self.sent = asyncio.Queue()

    async def accept(self) -> None:
        self._connected = True

    async def close(self) -> None:
        self._closed = True
        self._connected = False

    async def send_json(self, data: dict[str, Any]) -> None:
        if not self._connected:
            raise RuntimeError("WebSocket is not connected")
        self.received.put_nowait(data)

    async def iter_json(self) -> AsyncIterator[dict[str, Any]]:
        while self._connected:
            try:
                yield await asyncio.wait_for(self.sent.get(), 0.1)
            except TimeoutError:
                continue
            except Exception:
                break


class MockWSManager(WSManager):
    def __init__(self):
        self._rooms: dict[str | int, dict[str | int, MockWebSocket]] = {}
        super().__init__(self._rooms)

    def get_connection(self, member_id: str | int, room_id: str | int) -> MockWebSocket:
        return self._get_connection(member_id, room_id)

    def create_connection(
        self,
        member_id: str | int,
        room_id: str | int,
    ) -> MockWebSocket:
        ws = MockWebSocket()
        self._rooms.setdefault(room_id, {})[member_id] = ws
        return ws


@pytest.fixture
async def ws_manager(lobby: LobbySchema) -> MockWSManager:
    mock_ws_manager = MockWSManager()
    room_id = str(lobby.id)
    members = {}
    for player in lobby.players:
        member_id = player.user_id
        ws = MockWebSocket()
        members[player.user_id] = ws
        await ws.accept()
        await mock_ws_manager.add_connection(
            member_id=member_id,
            room_id=room_id,
            connection=ws,
        )
    return mock_ws_manager


@pytest.fixture
async def lead_conn(lobby: LobbySchema, ws_manager: MockWSManager) -> MockWebSocket:
    return ws_manager.get_connection(
        member_id=lobby.get_lead().user_id,
        room_id=str(lobby.id),
    )


@pytest.fixture
async def first_conn(lobby: LobbySchema, ws_manager: MockWSManager) -> MockWebSocket:
    return ws_manager.get_connection(
        member_id=lobby[2].user_id,
        room_id=str(lobby.id),
    )


@pytest.fixture
async def second_conn(lobby: LobbySchema, ws_manager: MockWSManager) -> MockWebSocket:
    return ws_manager.get_connection(
        member_id=lobby[3].user_id,
        room_id=str(lobby.id),
    )


@pytest.fixture
async def lobby_dal(redis_client: Redis) -> LobbyDAL:
    return LobbyDAL(redis_manager=RedisManager(client=redis_client))


@pytest.fixture
async def lead_player_game(
    lobby: LobbySchema,
    lobby_dal: LobbyDAL,
    ws_manager: MockWSManager,
) -> GameFlowService:
    flow_service = GameFlowService(ws_manager=ws_manager, lobby_dal=lobby_dal)
    lead = lobby.get_lead()
    flow_service.player = lead
    flow_service.lobby_id = lobby.id
    flow_service.lobby = lobby
    return flow_service


@pytest.fixture
async def first_player_game(
    lobby: LobbySchema,
    lobby_dal: LobbyDAL,
    ws_manager: MockWSManager,
) -> GameFlowService:
    flow_service = GameFlowService(ws_manager=ws_manager, lobby_dal=lobby_dal)
    first_player = lobby[2]
    flow_service.player = first_player
    flow_service.lobby_id = lobby.id
    flow_service.lobby = lobby
    return flow_service


@pytest.fixture
async def second_player_game(
    lobby: LobbySchema,
    lobby_dal: LobbyDAL,
    ws_manager: MockWSManager,
) -> GameFlowService:
    flow_service = GameFlowService(ws_manager=ws_manager, lobby_dal=lobby_dal)
    second_player = lobby[3]
    flow_service.player = second_player
    flow_service.lobby_id = lobby.id
    flow_service.lobby = lobby
    return flow_service
