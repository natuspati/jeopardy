from typing import List

from fastapi import Path, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.api.dependencies.database import get_repository
from app.api.dependencies.lobby import get_lobby_by_id_from_path
from app.db.repositories.players import PlayerRepository

from app.models.lobby import LobbyInDB
from app.models.player import PlayerPublic


async def get_player_by_id_from_path(
        player_id: str = Path(...),
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository)),
) -> PlayerPublic:
    player = await player_repo.get_player_by_id(
        lobby_id=lobby.id,
        player_id=player_id
    )
    
    if not player:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No question found with id: {player_id} in the category",
        )
    
    return player


async def list_players_for_lobby_by_id_from_path(
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path),
        player_repo: PlayerRepository = Depends(get_repository(PlayerRepository)),
) -> List[PlayerPublic]:
    return await player_repo.list_players_for_lobby(lobby_id=lobby.id)
