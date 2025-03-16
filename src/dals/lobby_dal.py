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

    async def select_by_id(self, lobby_id: int) -> LobbySchema | None:
        lobby = await self._redis.get(lobby_id=lobby_id)
        if lobby is not None:
            return validate_json(lobby, LobbySchema)

    async def select(self, offset: int, limit: int) -> list[LobbySchema]:
        lobbies = await self._redis.select(offset=offset, limit=limit)
        return [validate_json(lobby, LobbySchema) for lobby in lobbies]

    async def create(self, lobby_create: LobbyCreateSchema) -> LobbySchema:
        await self._redis.set(
            value=lobby_create.model_dump_json(),
            lobby_id=lobby_create.lobby_id,
        )
        return await self.select_by_id(lobby_create.lobby_id)

    async def update(self, lobby_update: LobbyUpdateSchema) -> LobbySchema:
        await self._redis.set(
            value=lobby_update.model_dump_json(),
            lobby_id=lobby_update.lobby_id,
        )
        return await self.select_by_id(lobby_update.lobby_id)
