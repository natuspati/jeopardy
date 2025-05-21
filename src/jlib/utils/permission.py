from typing import Any

from jlib.enums import LobbyMemberTypeEnum, LobbyStateEnum
from jlib.errors.game_flow import GameFlowError, InvalidGameStateError
from jlib.schemas.lobby import LobbySchema
from jlib.schemas.player import PlayerSchema
from jlib.schemas.prompt import PromptInGameSchema


class ActionChecker:
    def __init__(self, *, lobby: LobbySchema, player: PlayerSchema):
        self._lobby = lobby
        self._player = player

    def check_start(self) -> None:
        if self._player.type != LobbyMemberTypeEnum.LEAD:
            raise GameFlowError(f"Player {self._player.username} is not a lead")
        if self._lobby.state != LobbyStateEnum.CREATE:
            raise GameFlowError("Lobby has already started")

    def check_select_player(self, **message: Any) -> PlayerSchema:
        if self._player.type != LobbyMemberTypeEnum.LEAD:
            raise GameFlowError(f"Player {self._player.username} is not a lead")

        if self._lobby.state not in {LobbyStateEnum.START, LobbyStateEnum.SELECT_PLAYER}:
            raise GameFlowError("Cannot select player")

        selected_player = self._lobby.selected
        if selected_player:
            raise GameFlowError(f"Player {selected_player.user_id} is already selected")

        user_id = message.get("user_id")
        if not user_id:
            raise GameFlowError("Invalid message, user_id missing")

        player = self._lobby[user_id]
        if not player:
            raise GameFlowError(f"Player {user_id} is not found in the lobby")
        return player

    def check_select_question(self, **message: Any) -> PromptInGameSchema:
        selected_player = self._lobby.selected
        if not selected_player:
            raise InvalidGameStateError("No selected player when selecting question")

        if self._player.user_id != selected_player.user_id:
            raise GameFlowError(f"Player {self._player.user_id} is not selected player")

        if self._lobby.state != LobbyStateEnum.SELECT_QUESTION:
            raise GameFlowError("Cannot select question")

        prompt_id = message.get("prompt_id")
        if not prompt_id:
            raise GameFlowError("Invalid message, prompt_id missing")

        prompt = self._lobby.get_prompt(prompt_id)
        if not prompt:
            raise GameFlowError(f"Prompt {prompt_id} is not found in the lobby")
        if not prompt.available:
            raise GameFlowError(f"Prompt {prompt_id} is not available")
        return prompt
