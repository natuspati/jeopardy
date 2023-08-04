from typing import List

from fastapi import APIRouter, Body, Depends

from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.api.dependencies.database import get_repository
from app.api.dependencies.lobby import get_lobby_by_id_from_path
from app.api.dependencies.player import (
    list_players_for_lobby_by_id_from_path,
    get_player_by_name_from_path,
    check_player_modification_permissions
)
from app.api.dependencies.auth import get_current_active_user
from app.db.repositories.players import PlayerRepository

from app.models.lobby import LobbyInDB
from app.models.player import PlayerPublic, PlayerCreate, PlayerUpdate
from app.models.user import UserInDB

router = APIRouter()


@router.get(
    "/",
    response_model=List[PlayerPublic],
    response_description="List all players in a lobby",
    name="player:get-players-in-lobby"
)
async def list_players_in_lobby(
        players: List[PlayerPublic] = Depends(list_players_for_lobby_by_id_from_path),
) -> List[PlayerPublic]:
    return players


@router.get(
    "/{player_name}/",
    response_model=PlayerPublic,
    response_description="Get player by name",
    name="player:get-by-name"
)
async def get_player_by_id(
        player: PlayerPublic = Depends(get_player_by_name_from_path),
) -> PlayerPublic:
    return player


@router.post(
    "/",
    response_model=PlayerPublic,
    status_code=HTTP_201_CREATED,
    response_description="Add player to a lobby",
    name="player:add-to-lobby"
)
async def add_player_to_lobby(
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        current_user: UserInDB = Depends(get_current_active_user),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository))
) -> PlayerPublic:
    return await player_repo.create_player(
        player=PlayerCreate(
            lobby_id=str(lobby.id),
            name=current_user.username
        )
    )


@router.put(
    "/{player_name}/",
    response_model=PlayerPublic,
    response_description="Update player score",
    name="player:update-score-by-name",
    dependencies=[Depends(check_player_modification_permissions)]
)
async def update_player_score_by_name(
        player_update: PlayerUpdate = Body(),
        player: PlayerPublic = Depends(get_player_by_name_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository))
) -> PlayerPublic:
    return await player_repo.update_player_score(
        player=player,
        player_update=player_update
    )


@router.delete(
    "/{player_name}",
    status_code=HTTP_204_NO_CONTENT,
    response_description="Delete player by name",
    name="player:delete-by-name",
    dependencies=[Depends(check_player_modification_permissions)]
)
async def delete_player_by_name(
        player: PlayerPublic = Depends(get_player_by_name_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository)),
) -> None:
    return await player_repo.delete_player_by_name(player=player)
