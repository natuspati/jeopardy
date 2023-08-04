from typing import List

from fastapi import Path, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from app.api.dependencies.database import get_repository
from app.api.dependencies.lobby import get_lobby_by_id_from_path
from app.api.dependencies.auth import get_current_active_user
from app.db.repositories.players import PlayerRepository

from app.models.lobby import LobbyInDB
from app.models.player import PlayerPublic
from app.models.user import UserInDB


async def get_player_by_name_from_path(
        player_name: str = Path(...),
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository)),
) -> PlayerPublic:
    player = await player_repo.get_player_by_name(
        lobby_id=lobby.id,
        player_name=player_name
    )
    
    if not player:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No player {player_name} exists in lobby id {lobby.id}",
        )
    
    return player


async def list_players_for_lobby_by_id_from_path(
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository)),
) -> List[PlayerPublic]:
    return await player_repo.list_players_for_lobby(lobby_id=lobby.id)


def check_player_modification_permissions(
        current_user: UserInDB = Depends(get_current_active_user),
        player: PlayerPublic = Depends(get_player_by_name_from_path)
) -> None:
    if not user_owns_player(user=current_user, player=player):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Users are only able to modify players that they created.",
        )


def user_owns_player(
        user: UserInDB,
        player: PlayerPublic
) -> bool:
    return player.user_id == str(user.id)
