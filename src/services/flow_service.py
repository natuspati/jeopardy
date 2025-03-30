import uuid
from typing import Annotated, Any

from fastapi import Depends, WebSocket, WebSocketDisconnect

from dals import LobbyDAL
from jlib.dals import BaseLobbyDAL
from jlib.enums import LobbyStateEnum
from jlib.enums.game import LobbyEventEnum
from jlib.errors.game_flow import GameFlowError, WrongActionError
from jlib.schemas.lobby import LobbySchema, LobbyUpdateSchema
from jlib.schemas.player import PlayerSchema
from jlib.services import BaseGameFlowService
from jlib.ws import WSManager, get_ws_manager


class GameFlowService(BaseGameFlowService):
    def __init__(
        self,
        ws_manager: Annotated[WSManager, Depends(get_ws_manager)],
        lobby_dal: Annotated[BaseLobbyDAL, Depends(LobbyDAL)],
    ):
        self._ws = ws_manager
        self._lobby_dal = lobby_dal
        self._player: PlayerSchema | None = None
        self._lobby_id: str | None = None
        self._lobby: LobbySchema | None = None

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
            await self._handle_message(message)

    async def _handle_message(self, message: dict[str, Any]) -> None:
        action = message.pop("action")
        if action:
            await self._handle_action(action, **message)

    async def _handle_action(self, action: str, **message: Any) -> None:
        await self._update_lobby()
        match action:
            case "start":
                await self._handle_start()
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

    async def _handle_disconnect(self) -> None:
        self.lobby.pop_player(self.player.user_id)
        await self._update_lobby(players=self.lobby.players)
        await self._ws.remove_connection(
            member_id=self.player.user_id,
            room_id=self.lobby_id,
        )

    async def _handle_start(self) -> None:
        await self._update_lobby(state=LobbyStateEnum.START)
        await self._send()

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
        players: list[PlayerSchema | None] = None,
    ) -> None:
        if state or players:
            await self._lobby_dal.update(
                LobbyUpdateSchema(id=self.lobby_id, state=state, players=players),
            )
        self.lobby = await self._get_lobby()
