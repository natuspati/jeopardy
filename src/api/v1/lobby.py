import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, status

from auth.auth_utils import get_current_user, get_current_user_from_query
from jlib.schemas.lobby import (
    LobbyCreateShowSchema,
    LobbyJoinSchema,
    PaginatedBasicLobbySchema,
)
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.user import UserSchema
from jlib.services import BaseLobbyService
from services import LobbyService

router = APIRouter(prefix="/lobby", tags=["game"])


@router.get("", response_model=PaginatedBasicLobbySchema)
async def get_lobbies(
    pagination: Annotated[PaginationSchema, Query()],
    lobby_service: Annotated[BaseLobbyService, Depends(LobbyService)],
):
    return await lobby_service.get_lobbies(pagination)


@router.post("", response_model=LobbyJoinSchema, status_code=status.HTTP_201_CREATED)
async def create_lobby(
    lobby_create: LobbyCreateShowSchema,
    user: Annotated[UserSchema, Depends(get_current_user)],
    lobby_service: Annotated[BaseLobbyService, Depends(LobbyService)],
):
    return await lobby_service.create_lobby(user, lobby_create)


@router.websocket("/{lobby_id}/join")
async def join_lobby(
    lobby_id: uuid.UUID,
    user: Annotated[UserSchema, Depends(get_current_user_from_query)],
    websocket: WebSocket,
    lobby_service: Annotated[BaseLobbyService, Depends(LobbyService)],
):
    await lobby_service.join_lobby(
        lobby_id=str(lobby_id),
        user=user,
        connection=websocket,
    )
