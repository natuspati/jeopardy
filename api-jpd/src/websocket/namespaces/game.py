import logging
from typing import Any
from urllib.parse import parse_qs

import socketio

from errors.request import BadRequestError, NotFoundError
from services.dependencies import get_lobby_service

_logger = logging.getLogger(__name__)


class GameNamespace(socketio.AsyncNamespace):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lobby_service = get_lobby_service()

    async def on_connect(self, sid: str, environ: dict[str, Any]) -> bool:
        try:
            lobby_id = self._get_lobby_from_environment(environ)
        except BadRequestError as error:
            _logger.info(f"Client {sid} rejected: {error.detail}")
            return False

        try:
            await self._lobby_service.get_lobby(lobby_id)
        except NotFoundError:
            _logger.info(f"Client {sid} rejected: no lobby with ID {lobby_id}")
            return False

        
        return True

    async def on_disconnect(self, sid: str, reason: Any) -> None:
        _logger.info(f"Client {sid} disconnected")

    async def _join_game(self, sid: str, lobby_id: int) -> None:
        await self.enter_room(sid=sid, room=self._get_room(lobby_id))
        _logger.info(f"Client {sid} connected to lobby {lobby_id}")
        await self.emit("player_joined", )

    async def _get_game_state(self):
        pass
    
    async def _set_game_state(self):
        pass

    @classmethod
    def _get_lobby_from_environment(cls, environ: dict[str, Any]) -> int:
        query_string = environ.get("QUERY_STRING")
        if not query_string:
            raise BadRequestError("No query parameters provided")

        query_params = parse_qs(query_string)
        lobby_ids = query_params.get("lobby_id")
        if not lobby_ids or len(lobby_ids) > 1:
            raise BadRequestError("Invalid lobby_id in query parameters")

        try:
            lobby_id = int(lobby_ids[0])
        except ValueError as error:
            raise BadRequestError(f"Invalid lobby ID {lobby_ids[0]}") from error

        _logger.info(f"Lobby id: {lobby_id}")
        return lobby_id

    @classmethod
    def _get_room(cls, lobby_id: int) -> str:
        return f"lobby:id={lobby_id}"
