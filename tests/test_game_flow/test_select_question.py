import pytest
from fixtures.websocket_fixtures import MockWebSocket

from jlib.enums import LobbyStateEnum
from jlib.errors.game_flow import GameFlowError
from services.flow_service import GameFlowService


async def test_select_question(
    first_player_game: GameFlowService,
    second_player_game: GameFlowService,
    first_conn: MockWebSocket,
):
    prompt = next(p for p in first_player_game.lobby.categories[0].prompts)
    prompt.available = False
    await first_player_game._update_lobby(categories=first_player_game.lobby.categories)

    # No selected player forces select player lobby state.
    await first_player_game._handle_select_question(prompt_id=prompt.id)
    msg = first_conn.received.get_nowait()
    assert msg["error"]
    assert msg["lobby"]["state"] == LobbyStateEnum.SELECT_PLAYER

    player = first_player_game.lobby[first_player_game.player.user_id]
    player.selected = True

    # Non-selected players fail.
    await second_player_game._update_lobby(players=first_player_game.lobby.players)
    with pytest.raises(GameFlowError):
        await second_player_game._handle_select_question(prompt_id=prompt.id)

    # Invalid state fails.
    await first_player_game._update_lobby(players=first_player_game.lobby.players)
    with pytest.raises(GameFlowError):
        await first_player_game._handle_select_question(prompt_id=prompt.id)

    # Prompt not found fails.
    await first_player_game._update_lobby(state=LobbyStateEnum.SELECT_QUESTION)
    with pytest.raises(GameFlowError):
        await first_player_game._handle_select_question(prompt_id=prompt.id + 1000)

    # Prompt is not available, fails.
    with pytest.raises(GameFlowError):
        await first_player_game._handle_select_question(prompt_id=prompt.id)

    # Prompt is available, success.
    prompt = first_player_game.lobby.get_prompt(prompt_id=prompt.id)
    prompt.available = True
    await first_player_game._update_lobby(categories=first_player_game.lobby.categories)
    await first_player_game._handle_select_question(prompt_id=prompt.id)
    msg = first_conn.received.get_nowait()
    assert msg["event"] == LobbyStateEnum.ANSWER_QUESTION.value
    assert msg["lobby"]["state"] == LobbyStateEnum.ANSWER_QUESTION.value
