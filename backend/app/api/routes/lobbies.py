from typing import List

from fastapi import APIRouter, Body, Depends

from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.api.dependencies.database import get_repository
from app.api.dependencies.lobby import get_lobby_by_id_from_path, check_lobby_modification_permissions
from app.api.dependencies.auth import get_current_active_user
from app.db.repositories.lobbies import LobbyRepository
from app.models.lobby import LobbyInDB, LobbyCreate, LobbyPublic
from app.models.user import UserInDB

router = APIRouter()


@router.get(
    "/",
    response_model=List[LobbyInDB],
    response_description="List active lobbies",
    name="lobby:get-active"
)
async def list_active_lobbies(
        lobby_repo: LobbyRepository = Depends(get_repository(LobbyRepository))
) -> List[LobbyInDB]:
    return await lobby_repo.list_active_lobbies()


@router.get(
    "/{lobby_id}/",
    response_model=LobbyInDB,
    response_description="Get lobby by id",
    name="lobby:get-by-id"
)
async def get_lobby_by_id(
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
) -> LobbyInDB:
    return lobby


@router.post(
    "/",
    response_model=LobbyPublic,
    status_code=HTTP_201_CREATED,
    response_description="Create a new lobby",
    name="lobby:create"
)
async def create_new_lobby(
        lobby_repo: LobbyRepository = Depends(get_repository(LobbyRepository)),
        current_user: UserInDB = Depends(get_current_active_user)
) -> LobbyPublic:
    return await lobby_repo.create_lobby(lobby=LobbyCreate(owner=current_user.username))


@router.delete(
    "/{lobby_id}",
    status_code=HTTP_204_NO_CONTENT,
    response_description="Delete lobby by id",
    name="lobby:delete-by-id",
    dependencies=[Depends(check_lobby_modification_permissions)]
)
async def list_all_lobbies(
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        lobby_repo: LobbyRepository = Depends(get_repository(LobbyRepository)),
) -> None:
    return await lobby_repo.delete_lobby_by_id(lobby=lobby)
