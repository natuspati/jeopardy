from abc import ABC, abstractmethod

from jlib.schemas.lobby import LobbyCreateSchema, LobbySchema, LobbyUpdateSchema


class BaseLobbyDAL(ABC):
    @abstractmethod
    async def select_by_id(self, lobby_id: str) -> LobbySchema | None:
        pass

    @abstractmethod
    async def select(self, offset: int, limit: int) -> list[LobbySchema]:
        pass

    @abstractmethod
    async def create(self, lobby_create: LobbyCreateSchema) -> LobbySchema:
        pass

    @abstractmethod
    async def update(self, lobby_update: LobbyUpdateSchema) -> LobbySchema:
        pass
