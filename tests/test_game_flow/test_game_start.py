import pytest
from fixtures.websocket_fixtures import MockWebSocket

from jlib.enums.game import LobbyStateEnum
from jlib.errors.game_flow import GameFlowError
from services.flow_service import GameFlowService


async def test_game_start(
    lead_player_game: GameFlowService,
    lead_conn: MockWebSocket,
    first_conn: MockWebSocket,
    second_conn: MockWebSocket,
):
    await lead_player_game._handle_start()
    start_message = lead_conn.received.get_nowait()
    assert start_message
    assert start_message.get("event") == LobbyStateEnum.START.value
    assert start_message["lobby"].get("state") == LobbyStateEnum.START.value
    assert first_conn.received.get_nowait() == start_message
    assert second_conn.received.get_nowait() == start_message


async def test_non_lead_players_cannot_start(
    first_player_game: GameFlowService,
    second_player_game: GameFlowService,
    first_conn: MockWebSocket,
    second_conn: MockWebSocket,
):
    for game in (first_player_game, second_player_game):
        with pytest.raises(GameFlowError):
            await game._handle_start()


async def test_cannot_start_game_again(
    lead_player_game: GameFlowService,
    lead_conn: MockWebSocket,
):
    await lead_player_game._handle_start()
    with pytest.raises(GameFlowError):
        await lead_player_game._handle_start()
