from typing import Annotated

from fastapi import Depends, Request

from enums.lobby import LobbyStateEnum
from errors.auth import ForbiddenError
from errors.request import BadRequestError, NotFoundError
from repositories import LobbyRepo
from schemas.lobby.base import (
    BaseLobbySchema,
    LobbyCreatePublicSchema,
    LobbyCreateSchema,
    LobbySearchSchema,
    LobbyStartedPublicSchema,
)
from schemas.lobby.nested import LobbySchema
from services.category import CategoryService
from services.game import GameService


class LobbyService:
    def __init__(
        self,
        request: Request,
        lobby_repo: Annotated[LobbyRepo, Depends()],
        category_service: Annotated[CategoryService, Depends()],
        game_service: Annotated[GameService, Depends()],
    ):
        self._request = request
        self._lobby_repo = lobby_repo
        self._category_service = category_service
        self._game_service = game_service

    async def get_lobby(self, lobby_id: int) -> LobbySchema:
        lobby = await self._lobby_repo.select(lobby_id)
        if not lobby:
            raise NotFoundError(f"Lobby {lobby_id} not found")
        return lobby

    async def search_lobbies(self, search: LobbySearchSchema) -> list[LobbySchema]:
        return await self._lobby_repo.filter(search)

    async def create_lobby(self, lobby: LobbyCreatePublicSchema, user_id: int) -> BaseLobbySchema:
        categories = await self._category_service.search_categories(category_ids=lobby.category_ids)

        missing_category_ids = {cat.id for cat in categories} - set(lobby.category_ids)
        if missing_category_ids:
            raise BadRequestError(f"Missing categories: {missing_category_ids}")

        invalid_category_ids = {cat.id for cat in categories if not cat.is_valid}
        if invalid_category_ids:
            raise BadRequestError(f"Invalid categories: {invalid_category_ids}")

        lobby_with_host = LobbyCreateSchema(host_id=user_id, **lobby.model_dump())
        return await self._lobby_repo.insert(lobby_with_host)

    async def start_lobby(self, lobby_id: int, user_id: int) -> LobbyStartedPublicSchema:
        lobby = await self.get_lobby(lobby_id=lobby_id)

        if lobby.host_id != user_id:
            raise ForbiddenError(f"Lobby {lobby_id} does not belong to user {user_id}")

        if lobby.state != LobbyStateEnum.CREATED:
            raise BadRequestError(f"Lobby {lobby_id} has been started already")

        started_lobby = await self._lobby_repo.update(
            lobby_id=lobby_id,
            state=LobbyStateEnum.STARTED,
        )
        await self._game_service.create_game(started_lobby)
        return LobbyStartedPublicSchema(
            game_url=self._get_game_url(lobby_id),
            **started_lobby.model_dump(),
        )

    async def delete_lobby(self, lobby_id: int, user_id: int) -> None:
        lobby = await self.get_lobby(lobby_id=lobby_id)
        if lobby.host_id != user_id:
            raise ForbiddenError(f"Lobby {lobby_id} is not hosted by user {user_id}")
        await self._lobby_repo.delete(lobby_id)

    def _get_game_url(self, lobby_id: int) -> str:
        base_url = str(self._request.base_url).rstrip("/")
        return f"{base_url}/game?id={lobby_id}"
