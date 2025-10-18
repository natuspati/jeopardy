from typing import Annotated

from fastapi import Depends

from errors.auth import ForbiddenError
from errors.request import BadRequestError, NotFoundError
from repositories import LobbyRepo
from schemas.lobby.base import (
    BaseLobbySchema,
    LobbyCreatePublicSchema,
    LobbyCreateSchema,
    LobbySearchSchema,
)
from schemas.lobby.nested import LobbySchema
from services.category import CategoryService


class LobbyService:
    def __init__(
        self,
        lobby_repo: Annotated[LobbyRepo, Depends()],
        category_service: Annotated[CategoryService, Depends()],
    ):
        self._lobby_repo = lobby_repo
        self._category_service = category_service

    async def get_lobby(self, lobby_id: int) -> LobbySchema:
        lobby = await self._lobby_repo.select(lobby_id)
        if not lobby:
            raise NotFoundError(f"Lobby {lobby_id} not found")
        return lobby

    async def search_lobbies(self, search: LobbySearchSchema) -> list[LobbySchema]:
        return await self._lobby_repo.filter(search)

    async def create_lobby(self, lobby: LobbyCreatePublicSchema, user_id: int) -> BaseLobbySchema:
        categories = await self._category_service.search_categories(category_ids=lobby.category_ids)
        if len(categories) != len(lobby.category_ids):
            raise BadRequestError("Invalid categories")
        lobby_with_host = LobbyCreateSchema(host_id=user_id, **lobby.model_dump())
        return await self._lobby_repo.insert(lobby_with_host)

    async def delete_lobby(self, lobby_id: int, user_id: int) -> None:
        lobby = await self.get_lobby(lobby_id=lobby_id)
        if lobby.host_id != user_id:
            raise ForbiddenError(f"Lobby {lobby_id} is not hosted by user {user_id}")
        await self._lobby_repo.delete(lobby_id)
