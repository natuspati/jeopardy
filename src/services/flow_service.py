import logging
import uuid
from typing import Annotated, Any

from fastapi import Depends, WebSocket, WebSocketDisconnect

from dals import LobbyDAL
from jlib.dals import BaseLobbyDAL
from jlib.enums import LobbyStateEnum
from jlib.enums.game import LobbyEventEnum
from jlib.errors.game_flow import GameFlowError, InvalidGameStateError, WrongActionError
from jlib.schemas.category import CategoryInGameSchema
from jlib.schemas.lobby import LobbySchema, LobbyUpdateSchema
from jlib.schemas.player import PlayerSchema
from jlib.services import BaseGameFlowService
from jlib.utils.permission import ActionChecker
from jlib.ws import WSManager, get_ws_manager

_logger = logging.getLogger(__name__)


class GameFlowService(BaseGameFlowService):
    def __init__(
        self,
        ws_manager: Annotated[WSManager, Depends(get_ws_manager)],
        lobby_dal: Annotated[BaseLobbyDAL, Depends(LobbyDAL)],
    ):
        self._ws: Any = ws_manager
        self._lobby_dal = lobby_dal
        self._player: PlayerSchema | None = None
        self._lobby_id: str | None = None
        self._lobby: LobbySchema | None = None
        self._checker = ActionChecker

    @property
    def player(self) -> PlayerSchema:
        if self._player is None:
            raise GameFlowError(f"Player {self.player.username} is not set")
        return self._player

    @player.setter
    def player(self, player: PlayerSchema):
        self._player = player

    @property
    def lobby_id(self) -> str:
        return self._lobby_id

    @lobby_id.setter
    def lobby_id(self, lobby_id: str | uuid.UUID) -> None:
        self._lobby_id = str(lobby_id)

    @property
    def lobby(self) -> LobbySchema:
        if self._lobby is None:
            raise GameFlowError(f"Lobby {self.lobby_id} is not set")
        return self._lobby

    @lobby.setter
    def lobby(self, lobby: LobbySchema) -> None:
        self._lobby = lobby

    @property
    def checker(self) -> ActionChecker:
        return self._checker(lobby=self._lobby, player=self.player)

    async def play(self, new_player: PlayerSchema, connection: WebSocket) -> None:
        self.player = new_player
        self.lobby_id = new_player.lobby_id
        self.lobby = await self._get_lobby()
        await self._handle_join(connection)
        try:
            await self._listen()
        except WebSocketDisconnect:
            await self._handle_disconnect()

    async def _listen(self):
        receiver = await self._ws.get_receiver(
            member_id=self.player.user_id,
            room_id=self.lobby_id,
        )
        async for message in receiver:
            try:
                await self._handle_message(message)
            except (GameFlowError, WrongActionError) as error:
                _logger.info(
                    f"Error: {error.detail}"
                    + f"Player: {self.player.user_id}, lobby: {self.lobby.id}"
                    + f"Player message: {message}",
                )
                await self._handle_game_error(error)

    async def _handle_message(self, message: dict[str, Any]) -> None:
        action = message.pop("action")
        if action:
            await self._handle_action(action, **message)

    async def _handle_action(self, action: str, **message: Any) -> None:
        await self._update_lobby()
        match action:
            case LobbyStateEnum.START:
                await self._handle_start()
            case LobbyStateEnum.SELECT_PLAYER:
                await self._handle_select_player(**message)
            case LobbyStateEnum.SELECT_QUESTION:
                await self._handle_select_question(**message)
            case LobbyStateEnum.ANSWER_QUESTION:
                await self._handle_answer_question()
            case _:
                raise WrongActionError(f"Unsupported action {action}")

    async def _handle_join(self, connection: WebSocket) -> None:
        await self._ws.add_connection(
            member_id=self.player.user_id,
            room_id=self.lobby_id,
            connection=connection,
        )
        await self._send(
            event=LobbyEventEnum.JOIN,
            message={"meta": f"Player {self.player.username} joined the lobby"},
        )

    async def _handle_start(self) -> None:
        self.checker.check_start()
        await self._update_lobby(state=LobbyStateEnum.START)
        await self._send()

    async def _handle_select_player(self, **message: Any) -> None:
        player = self.checker.check_select_player(**message)
        player.selected = True
        await self._update_lobby(state=LobbyStateEnum.SELECT_QUESTION, players=self.lobby.players)
        await self._send(message={"meta": f"Player {player.user_id} has been selected"})

    async def _handle_select_question(self, **message: Any) -> None:
        try:
            prompt = self.checker.check_select_question(**message)
        except InvalidGameStateError as error:
            await self._handle_state_error(error, LobbyStateEnum.SELECT_PLAYER)
        else:
            prompt.selected = False
            prompt.available = False
            await self._update_lobby(state=LobbyStateEnum.ANSWER_QUESTION)
            await self._send(message={"meta": f"Prompt {prompt.id} has been selected"})

    async def _handle_answer_question(self) -> None:
        self.checker.check_answer()
        await self._update_lobby(state=LobbyStateEnum.RATE_ANSWER)
        await self._send(
            message={"meta": f"Answer from player {self.player.user_id} has been selected"},
        )

    async def _handle_rate_answer(self, **message: Any) -> None:
        rating = self.checker.check_rate_answer(**message)
        selected_player = self.lobby.selected
        if rating:
            if selected_player:
                await self._update_lobby(state=LobbyStateEnum.SELECT_QUESTION)
                extra_message = {
                    "meta": f"Player {selected_player.user_id} continues to select question",
                }
                players = None
            else:
                selected_player = self.lobby[self.player.user_id]
                selected_player.selected = True
                players = self.lobby.players
                extra_message = {"meta": f"Player {selected_player.user_id} has been selected"}
            await self._update_lobby(state=LobbyStateEnum.SELECT_QUESTION, players=players)
            await self._send(message=extra_message)
        else:
            if selected_player:
                selected_player.selected = False
                players = self.lobby.players
                extra_message = {"meta": f"Player {selected_player.user_id} has been unselected"}
            else:
                players = None
                extra_message = None
            await self._update_lobby(state=LobbyStateEnum.ANSWER_QUESTION, players=players)
            await self._send(message=extra_message)

    async def _handle_game_error(self, error: GameFlowError) -> None:
        await self._send(
            self.player.user_id,
            event=LobbyEventEnum.ERROR,
            message={"error": error.detail},
            include_lobby=False,
        )

    async def _handle_state_error(
        self,
        error: InvalidGameStateError,
        desired_state: LobbyStateEnum,
    ) -> None:
        await self._update_lobby(state=desired_state)
        await self._send(
            event=LobbyEventEnum.ERROR,
            message={"error": error.detail},
            include_lobby=True,
        )

    async def _handle_disconnect(self) -> None:
        self.lobby.pop_player(self.player.user_id)
        await self._update_lobby(players=self.lobby.players)
        await self._ws.remove_connection(
            member_id=self.player.user_id,
            room_id=self.lobby_id,
        )

    async def _send(
        self,
        *player_ids: int,
        event: LobbyEventEnum | None = None,
        message: dict[str, Any] | None = None,
        include_lobby: bool = True,
    ) -> None:
        if message is None:
            message = {}
        if event is None:
            event = self.lobby.state
        message["event"] = event.value
        if include_lobby:
            message.setdefault("lobby", self.lobby.model_dump(mode="json"))
        await self._ws.send_json(*player_ids, room_id=self.lobby_id, data=message)

    async def _get_lobby(self) -> LobbySchema:
        return await self._lobby_dal.select_by_id(self.lobby_id)

    async def _update_lobby(
        self,
        *,
        state: LobbyStateEnum | None = None,
        players: list[PlayerSchema] | None = None,
        categories: list[CategoryInGameSchema] | None = None,
    ) -> None:
        if state or players or categories:
            lobby_update = {"id": self.lobby_id}
            if state:
                lobby_update["state"] = state
            if players:
                lobby_update["players"] = players
            if categories:
                lobby_update["categories"] = categories

            await self._lobby_dal.update(LobbyUpdateSchema(**lobby_update))
        self.lobby = await self._get_lobby()
        _logger.info(f"Updated lobby {self.lobby_id} state")
