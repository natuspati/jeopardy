from abc import ABC, abstractmethod

from fastapi import WebSocket

from jlib.schemas.player import PlayerSchema


class BaseGameFlowService(ABC):
    @abstractmethod
    async def play(self, player: PlayerSchema, connection: WebSocket) -> None:
        pass
