from abc import ABC, abstractmethod

from jlib.schemas.lobby import LobbyCreateSchema, LobbySchema, LobbyUpdateSchema


class BaseLobbyDAL(ABC):
    @abstractmethod
    async def select_by_id(self, lobby_id: int) -> LobbySchema | None:
        pass

    @abstractmethod
    async def select(self, offset: int, limit: int) -> list[LobbySchema]:
        pass

    @abstractmethod
    async def create(self, lobby_create: LobbyCreateSchema):
        pass

    @abstractmethod
    async def update(self, lobby_update: LobbyUpdateSchema):
        pass
