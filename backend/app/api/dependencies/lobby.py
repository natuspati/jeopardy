from fastapi import Path, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.api.dependencies.database import get_repository
from app.db.repositories.lobbies import LobbyRepository
from app.models.lobby import LobbyInDB


async def get_lobby_by_id_from_path(
        lobby_id: str = Path(...),
        lobby_repo: LobbyRepository = Depends(get_repository(LobbyRepository)),
) -> LobbyInDB:
    lobby = await lobby_repo.get_lobby_by_id(lobby_id=lobby_id)
    
    if not lobby:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No lobby found with that id.",
        )
    
    return lobby
