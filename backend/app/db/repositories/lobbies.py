from typing import List, Optional

from bson import ObjectId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories.base import BaseRepository
from app.db.repositories.players import PlayerRepository
from app.models.core import PyObjectId
from app.models.lobby import LobbyPublic, LobbyCreate, LobbyInDB
from app.models.user import UserInDB

COLLECTION_CONFIG = {
    "name": "lobbies"
}


class LobbyRepository(BaseRepository):
    """"
    All database actions associated with the Lobby resource
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = self.db.get_collection(COLLECTION_CONFIG["name"])
        self.player_repo = PlayerRepository(db)
    
    async def list_active_lobbies(self) -> List[LobbyPublic]:
        return await self._list_lobbies_by_active_status(active=True)
    
    async def list_inactive_lobbies(self) -> List[LobbyPublic]:
        return await self._list_lobbies_by_active_status(active=False)
    
    async def _list_lobbies_by_active_status(self, *, active: bool) -> List[LobbyPublic]:
        lobby_records = await self.collection.find(
            {"active": active}
        ).to_list(1000)
        return [LobbyPublic(**lobby) for lobby in lobby_records]
    
    async def get_lobby_by_id(
            self,
            *,
            lobby_id: str | PyObjectId,
            only_active: bool = True
    ) -> Optional[LobbyPublic]:
        query = {
            "_id": ObjectId(lobby_id) if isinstance(lobby_id, str) else lobby_id
        }
        if only_active:
            query["active"] = True
        
        fetched_lobby = await self.collection.find_one(query)
        if fetched_lobby:
            return LobbyPublic(**fetched_lobby)
    
    async def create_lobby(
            self,
            *,
            lobby: LobbyCreate
    ) -> LobbyPublic:
        create_data = lobby.model_dump()
        
        encoded_new_lobby = jsonable_encoder(create_data)
        inserted_new_lobby = await self.collection.insert_one(encoded_new_lobby)
        
        if not inserted_new_lobby.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on category {inserted_new_lobby.inserted_id} could not be acknowledged"
            )
        
        return await self.get_lobby_by_id(lobby_id=inserted_new_lobby.inserted_id)
    
    async def deactivate_lobby(
            self,
            *,
            lobby: LobbyInDB
    ):
        return await self._change_lobby_active_status(lobby=lobby, active=False)
    
    async def activate_lobby(
            self,
            *,
            lobby: LobbyInDB
    ):
        return await self._change_lobby_active_status(lobby=lobby, active=True)
    
    async def _change_lobby_active_status(
            self,
            *,
            lobby: LobbyInDB,
            active: bool
    ):
        updated_lobby = lobby.model_copy(update={"active": active})
        encoded_updated_lobby = jsonable_encoder(updated_lobby)
        
        inserted_lobby = await self.collection.update_one(
            {"_id": lobby.id}, {"$set": encoded_updated_lobby}
        )
        
        if not inserted_lobby.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on lobby {lobby.id} could not be acknowledged"
            )
        
        if (
                fetched_updated_lobby := await self.get_lobby_by_id(
                    lobby_id=lobby.id,
                    only_active=False
                )
        ) is None:
            raise HTTPException(status_code=404, detail=f"Lobby {lobby.id} not found")
        
        return fetched_updated_lobby
    
    async def delete_lobby_by_id(
            self,
            *,
            lobby: LobbyInDB
    ) -> None:
        delete_result = await self.collection.delete_one({"_id": lobby.id})
        
        if delete_result.deleted_count != 1:
            raise HTTPException(status_code=404, detail=f"Lobby {lobby.id} not found")
        
        # Delete players in the lobby
        await self.player_repo.delete_players_for_lobby(lobby_id=lobby.id)
