from typing import List, Optional

from fastapi import Path, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

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
    return await player_repo.list_players_in_lobby(lobby_id=lobby.id)


async def check_user_in_lobby(
        current_user: Optional[UserInDB] = Depends(get_current_active_user),
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository)),
) -> None:
    """
    Check if current user is either lobby owner or exists as a player in the lobby
    """
    if not current_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Users are only able to modify players that they created."
        )
    
    player_names = await player_repo.list_players_in_lobby(lobby_id=lobby.id, only_names=True)
    if current_user.username not in player_names and current_user.username != lobby.owner:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User must be lobby owner or player.",
        )


async def check_user_owns_player_in_lobby(
        current_user: Optional[UserInDB] = Depends(get_current_active_user),
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository)),
):
    """
    Check if current user owns a player in the lobby
    """
    if await player_repo.get_player_by_name(lobby_id=lobby.id, player_name=current_user.username):
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="User already owns a player in the lobby.",
        )


async def check_player_modification_permissions(
        current_user: Optional[UserInDB] = Depends(get_current_active_user),
        player: PlayerPublic = Depends(get_player_by_name_from_path)
) -> None:
    if not current_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Users are only able to modify players that they created."
        )
    if current_user.username != player.name:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Users are only able to modify players that they created.",
        )
