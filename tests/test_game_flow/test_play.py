import asyncio
from unittest.mock import AsyncMock, patch

from fixtures.websocket_fixtures import MockWebSocket, MockWSManager

from jlib.enums.game import LobbyEventEnum
from jlib.errors.game_flow import GameFlowError
from services.flow_service import GameFlowService


@patch("services.flow_service.GameFlowService._handle_message", new_callable=AsyncMock)
async def test_play_continues_if_game_error(
    handle_message_mock: AsyncMock,
    ws_manager: MockWSManager,
    lead_player_game: GameFlowService,
    lead_conn: MockWebSocket,
):
    error_message = "Test game error"
    handle_message_mock.side_effect = GameFlowError(detail=error_message)
    test_message = {"action": "some_action", "data": "test_data"}
    lead_conn.sent.put_nowait(test_message)

    listen_task = asyncio.create_task(lead_player_game._listen())
    await asyncio.sleep(0.1)
    lead_conn._connected = False
    await listen_task

    handle_message_mock.assert_called_once_with(test_message)
    error_response = lead_conn.received.get_nowait()
    assert error_response["event"] == LobbyEventEnum.ERROR.value
    assert error_response.get("error") == error_message
    assert not error_response.get("lobby")
