from fastapi import Path, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.lobbies import LobbyRepository
from app.models.lobby import LobbyInDB
from app.models.user import UserInDB


async def get_lobby_by_id_from_path(
        lobby_id: str = Path(...),
        lobby_repo: LobbyRepository = Depends(get_repository(LobbyRepository)),
) -> LobbyInDB:
    lobby = await lobby_repo.get_lobby_by_id(lobby_id=lobby_id, only_active=True)
    
    if not lobby:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No lobby found with that id.",
        )
    
    if not lobby.active:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="No lobby found with that id.",
        )
    
    return lobby


def check_lobby_modification_permissions(
        current_user: UserInDB = Depends(get_current_active_user),
        lobby: LobbyInDB = Depends(get_lobby_by_id_from_path)
) -> None:
    if current_user.username != lobby.owner:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Users are only able to modify lobbies that they created.",
        )

