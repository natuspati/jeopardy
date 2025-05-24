import pytest
from fixtures.websocket_fixtures import MockWebSocket

from jlib.enums import LobbyStateEnum
from jlib.errors.game_flow import GameFlowError
from services.flow_service import GameFlowService


async def test_answer_question(
    lead_player_game: GameFlowService,
    first_player_game: GameFlowService,
    first_conn: MockWebSocket,
):
    player = first_player_game.lobby[first_player_game.player.user_id]
    player.selected = True
    await first_player_game._update_lobby(players=first_player_game.lobby.players)

    # Another player cannot answer question.
    with pytest.raises(GameFlowError):
        await lead_player_game._handle_answer_question()

    # Invalid state fails.
    with pytest.raises(GameFlowError):
        await first_player_game._handle_answer_question()

    await first_player_game._update_lobby(state=LobbyStateEnum.ANSWER_QUESTION)
    await first_player_game._handle_answer_question()
    msg = first_conn.received.get_nowait()
    assert msg["event"] == LobbyStateEnum.RATE_ANSWER
    assert msg["lobby"]["state"] == LobbyStateEnum.RATE_ANSWER
