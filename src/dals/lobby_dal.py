import uuid
from typing import Annotated

from fastapi import Depends

from jlib.dals import BaseLobbyDAL
from jlib.redis import RedisManager
from jlib.schemas.lobby import LobbyCreateSchema, LobbySchema, LobbyUpdateSchema
from jlib.utils.validation import validate_json


class LobbyDAL(BaseLobbyDAL):
    def __init__(self, redis_manager: Annotated[RedisManager, Depends()]):
        self._redis = redis_manager
        self._redis.add_namespace("lobby")

    async def select_by_id(self, lobby_id: str | uuid.UUID) -> LobbySchema | None:
        lobby = await self._redis.get(lobby_id=str(lobby_id))
        if lobby is not None:
            return validate_json(lobby, LobbySchema)

    async def select(self, offset: int, limit: int) -> list[LobbySchema]:
        lobbies = await self._redis.select(offset=offset, limit=limit)
        return [validate_json(lobby, LobbySchema) for lobby in lobbies]

    async def create(self, lobby_create: LobbyCreateSchema) -> LobbySchema:
        await self._redis.set(
            value=lobby_create.model_dump_json(),
            lobby_id=str(lobby_create.id),
        )
        return await self.select_by_id(str(lobby_create.id))

    async def update(self, lobby_update: LobbyUpdateSchema) -> LobbySchema:
        existing_lobby = await self.select_by_id(lobby_update.id)
        if lobby_update.state is not None:
            existing_lobby.state = lobby_update.state
        if lobby_update.players is not None:
            existing_lobby.players = lobby_update.players

        await self._redis.set(
            value=existing_lobby.model_dump_json(),
            lobby_id=str(lobby_update.id),
        )
        return existing_lobby
