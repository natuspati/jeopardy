from typing import Annotated

from fastapi import APIRouter, Depends, Query

from jlib.schemas.lobby import LobbySchema
from jlib.schemas.pagination import PaginationSchema
from jlib.services import BaseLobbyService
from services import LobbyService

router = APIRouter(prefix="/lobby", tags=["game"])


@router.get("", response_model=list[LobbySchema])
async def get_lobbies(
    pagination: Annotated[PaginationSchema, Query()],
    lobby_service: Annotated[BaseLobbyService, Depends(LobbyService)],
):
    return await lobby_service.get_lobbies(pagination)
