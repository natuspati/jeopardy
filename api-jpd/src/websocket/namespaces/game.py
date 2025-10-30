import logging
from typing import Any
from urllib.parse import parse_qs

import socketio

from errors.request import NotFoundError
from services.dependencies import get_lobby_service

_logger = logging.getLogger(__name__)


class GameNamespace(socketio.AsyncNamespace):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lobby_service = get_lobby_service()

    async def on_connect(self, sid: str, environ: dict[str, Any]) -> bool:
        query_params = parse_qs(environ.get("QUERY_STRING", ""))
        lobby_id: str | None = query_params.get("lobby_id", [None])[0]
        _logger.info(f"Lobby id: {lobby_id}")

        # if not lobby_id:
        #     _logger.info(f"Connection from {sid} rejected: missing lobby_id.")
        #     return False
        # lobby_id: int = int(lobby_id)
        # try:
        #     lobby = await self._lobby_service.get_lobby(lobby_id)
        # except NotFoundError:
        #     _logger.info(f"Connection from {sid} rejected: no such lobby {lobby_id}")
        #     return False

        # await self.enter_room(sid=sid, room=lobby_id)
        # _logger.info(f"Client {sid} connected to lobby {lobby_id}")
        return True

    async def on_disconnect(self, sid: str) -> None:
        _logger.info(f"Client {sid} disconnected")
