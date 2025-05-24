import pytest
from fixtures.websocket_fixtures import MockWebSocket

from jlib.enums import LobbyStateEnum
from jlib.errors.game_flow import GameFlowError
from services.flow_service import GameFlowService


async def test_rate_answer(
    lead_player_game: GameFlowService,
    first_player_game: GameFlowService,
    lead_conn: MockWebSocket,
):
    # Non lead players cannot rate answer.
    with pytest.raises(GameFlowError):
        await first_player_game._handle_rate_answer(rating=True)

    # Invalid state fails.
    with pytest.raises(GameFlowError):
        await lead_player_game._handle_rate_answer(rating=True)

    await lead_player_game._update_lobby(state=LobbyStateEnum.RATE_ANSWER)
    # Invalid message fails.
    with pytest.raises(GameFlowError):
        await lead_player_game._handle_rate_answer(rate=True)

    # Non-selected player successfully answers question.
    # await lead_player_game._handle_rate_answer(rating=True)
    # msg = lead_conn.received.get_nowait()
    # print(msg)
