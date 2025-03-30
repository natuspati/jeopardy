from abc import ABC, abstractmethod

from starlette.websockets import WebSocket

from jlib.schemas.lobby import LobbyCreateShowSchema, PaginatedBasicLobbySchema
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.user import UserSchema


class BaseLobbyService(ABC):
    @abstractmethod
    async def get_lobbies(
        self,
        pagination: PaginationSchema,
    ) -> PaginatedBasicLobbySchema:
        pass

    @abstractmethod
    async def create_lobby(self, user: UserSchema, lobby_create: LobbyCreateShowSchema):
        pass

    @abstractmethod
    async def join_lobby(self, lobby_id: str, user: UserSchema, connection: WebSocket):
        pass
