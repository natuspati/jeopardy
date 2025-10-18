from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from auth import authenticate_user
from schemas.lobby.base import BaseLobbySchema, LobbyCreatePublicSchema, LobbySearchSchema
from schemas.lobby.nested import LobbySchema
from schemas.user.base import BaseUserSchema
from services import LobbyService

router = APIRouter(prefix="/lobby", tags=["lobby"])


@router.get("", response_model=list[LobbySchema])
async def search_lobbies(
    search: Annotated[LobbySearchSchema, Query()],
    lobby_service: Annotated[LobbyService, Depends()],
):
    return await lobby_service.search_lobbies(search)


@router.get("/{lobby_id}", response_model=LobbySchema)
async def get_lobby(
    lobby_id: int,
    lobby_service: Annotated[LobbyService, Depends()],
):
    return await lobby_service.get_lobby(lobby_id)


@router.post("", response_model=BaseLobbySchema, status_code=status.HTTP_201_CREATED)
async def create_lobby(
    lobby: LobbyCreatePublicSchema,
    lobby_service: Annotated[LobbyService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    return await lobby_service.create_lobby(lobby, user_id=user.id)


@router.delete("/{lobby_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_lobby(
    lobby_id: int,
    lobby_service: Annotated[LobbyService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    await lobby_service.delete_lobby(lobby_id, user_id=user.id)
