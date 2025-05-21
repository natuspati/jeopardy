import pytest
from fixtures.websocket_fixtures import MockWebSocket

from jlib.enums import LobbyMemberTypeEnum, LobbyStateEnum
from jlib.errors.game_flow import GameFlowError
from services.flow_service import GameFlowService


async def test_select_player(lead_player_game: GameFlowService, lead_conn: MockWebSocket):
    player = next(p for p in lead_player_game.lobby.players if p.type != LobbyMemberTypeEnum.LEAD)

    # Cannot select player in the wrong state.
    with pytest.raises(GameFlowError):
        await lead_player_game._handle_select_player(user_id=player.user_id)

    # Can select player in select player state.
    await lead_player_game._update_lobby(state=LobbyStateEnum.SELECT_PLAYER)
    await lead_player_game._handle_select_player(user_id=player.user_id)
    msg = lead_conn.received.get_nowait()
    fetched_player = next(p for p in msg["lobby"]["players"] if p["user_id"] == player.user_id)
    assert fetched_player["selected"]
    assert msg["event"] == LobbyStateEnum.SELECT_QUESTION.value
    assert msg["lobby"]["state"] == LobbyStateEnum.SELECT_QUESTION.value

    # Cannot select a new player when another already selected.
    another_player = next(
        p
        for p in lead_player_game.lobby.players
        if p.type != LobbyMemberTypeEnum.LEAD and p.user_id != player.user_id
    )
    with pytest.raises(GameFlowError):
        await lead_player_game._handle_select_player(user_id=another_player.user_id)


async def test_only_lead_select_player(first_player_game: GameFlowService):
    await first_player_game._update_lobby(state=LobbyStateEnum.SELECT_PLAYER)
    with pytest.raises(GameFlowError):
        await first_player_game._handle_select_player(user_id=first_player_game.player.user_id)
