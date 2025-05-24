import logging
from typing import Any

from jlib.enums import LobbyMemberTypeEnum, LobbyStateEnum
from jlib.errors.base import BaseError
from jlib.errors.game_flow import GameFlowError, InvalidGameStateError
from jlib.schemas.lobby import LobbySchema
from jlib.schemas.player import PlayerSchema
from jlib.schemas.prompt import PromptInGameSchema

_logger = logging.getLogger(__name__)


class ActionChecker:
    _default_error = GameFlowError

    def __init__(self, *, lobby: LobbySchema, player: PlayerSchema):
        self._lobby = lobby
        self._player = player

    def check_start(self) -> None:
        if self._player.type != LobbyMemberTypeEnum.LEAD:
            self._handle_error(f"Player {self._player.username} is not a lead")
        if self._lobby.state != LobbyStateEnum.CREATE:
            self._handle_error("Lobby has already started")

    def check_select_player(self, **message: Any) -> PlayerSchema:
        if self._player.type != LobbyMemberTypeEnum.LEAD:
            self._handle_error(f"Player {self._player.username} is not a lead")

        if self._lobby.state not in {
            LobbyStateEnum.START,
            LobbyStateEnum.SELECT_PLAYER,
        }:
            self._handle_error("Cannot select player")

        selected_player = self._lobby.selected
        if selected_player:
            self._handle_error(f"Player {selected_player.user_id} is already selected")

        user_id = message.get("user_id")
        if not user_id:
            self._handle_error("Invalid message, user_id missing")

        player = self._lobby[user_id]
        if not player:
            self._handle_error(f"Player {user_id} is not found in the lobby")
        return player

    def check_select_question(self, **message: Any) -> PromptInGameSchema:
        selected_player = self._lobby.selected
        if not selected_player:
            self._handle_error("No selected player when selecting question", InvalidGameStateError)

        if self._player.user_id != selected_player.user_id:
            self._handle_error(f"Player {self._player.user_id} is not selected player")

        if self._lobby.state != LobbyStateEnum.SELECT_QUESTION:
            self._handle_error("Cannot select question")

        prompt_id = message.get("prompt_id")
        if not prompt_id:
            self._handle_error("Invalid message, prompt_id missing")

        prompt = self._lobby.get_prompt(prompt_id)
        if not prompt:
            self._handle_error(f"Prompt {prompt_id} is not found in the lobby")
        if not prompt.available:
            self._handle_error(f"Prompt {prompt_id} is not available")
        return prompt

    def check_answer(self) -> None:
        selected_player = self._lobby.selected
        if selected_player and self._player.user_id != selected_player.user_id:
            self._handle_error(f"Player {self._player.user_id} is not selected player")
        if self._lobby.state != LobbyStateEnum.ANSWER_QUESTION:
            self._handle_error("Cannot answer question")

    def check_rate_answer(self, **message: Any) -> bool:
        if self._player.type != LobbyMemberTypeEnum.LEAD:
            self._handle_error(f"Player {self._player.username} is not a lead")

        if self._lobby.state != LobbyStateEnum.RATE_ANSWER:
            self._handle_error("Cannot rate answer")

        rating = message.get("rating")
        if rating is None:
            self._handle_error("Invalid message, rating missing")
        return rating

    @classmethod
    def _handle_error(cls, message: str, error_type: type[BaseError] | None = None):
        error = error_type(message) if error_type else cls._default_error(message)
        _logger.info(f"{error.__class__.__name__}: {message}")
        raise error
