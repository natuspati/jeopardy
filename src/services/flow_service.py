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
        self._lobby: LobbySchema | None = None

    @property
    def player(self) -> PlayerSchema:
        if self._player is None:
            raise GameFlowError(f"Player {self.player.username} is not set")
        return self._player

    @property
    def lobby_id(self) -> str:
        return str(self.player.lobby_id)

    @property
    def lobby(self) -> LobbySchema:
        if self._lobby is None:
            raise GameFlowError(f"Lobby {self.lobby_id} is not set")
        return self._lobby

    async def play(self, new_player: PlayerSchema, connection: WebSocket) -> None:
        self._player = new_player
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
        new_players = [
            p for p in self.lobby.players if p.user_id != self.player.user_id
        ]
        await self._lobby_dal.update(self._get_update_players(new_players))
        await self._ws.remove_connection(
            member_id=self.player.user_id,
            room_id=self.lobby_id,
        )

    async def _handle_start(self) -> None:
        await self._lobby_dal.update(self._get_update_state(LobbyStateEnum.START))
        await self._send()

    async def _send(
        self,
        *player_ids: int,
        event: LobbyEventEnum | None = None,
        message: dict[str, Any] | None = None,
        include_lobby: bool = True,
    ) -> None:
        lobby = await self._get_lobby()
        if message is None:
            message = {}
        if event is None:
            event = lobby.state
        message["event"] = event.value
        if include_lobby:
            message.setdefault("lobby", lobby.model_dump(mode="json"))
        await self._ws.send_json(*player_ids, room_id=self.lobby_id, data=message)

    async def _get_lobby(self) -> LobbySchema:
        return await self._lobby_dal.select_by_id(self.lobby_id)

    def _get_update_state(self, state: LobbyStateEnum) -> LobbyUpdateSchema:
        return LobbyUpdateSchema(id=self.lobby_id, state=state)

    def _get_update_players(self, players: list[PlayerSchema]) -> LobbyUpdateSchema:
        return LobbyUpdateSchema(id=self.lobby_id, players=players)
