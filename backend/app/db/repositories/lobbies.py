from typing import List

from bson import ObjectId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.db.repositories.base import BaseRepository
from app.models.core import PyObjectId
from app.models.lobby import LobbyPublic, LobbyCreate, LobbyInDB
from app.models.user import UserInDB


class LobbyRepository(BaseRepository):
    """"
    All database actions associated with the Lobby resource
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = self.db.get_collection("lobbies")
    
    async def list_all_lobbies(self) -> List[LobbyPublic]:
        lobby_records = await self.collection.find().to_list(1000)
        
        return [LobbyPublic(**lobby) for lobby in lobby_records]
    
    async def get_lobby_by_id(
            self,
            *,
            lobby_id: str | PyObjectId
    ) -> LobbyPublic:
        fetched_lobby = await self.collection.find_one(
            {"_id": ObjectId(lobby_id) if isinstance(lobby_id, str) else lobby_id}
        )
        return LobbyPublic(**fetched_lobby)
    
    async def create_lobby(
            self,
            *,
            lobby: LobbyCreate,
            current_user: UserInDB,
    ) -> LobbyPublic:
        create_data = lobby.model_dump()
        create_data["owner"] = current_user.id
        
        encoded_new_lobby = jsonable_encoder(create_data)
        inserted_new_lobby = await self.collection.insert_one(encoded_new_lobby)
        
        if not inserted_new_lobby.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on category {inserted_new_lobby.inserted_id} could not be acknowledged"
            )
        
        return await self.get_lobby_by_id(lobby_id=inserted_new_lobby.inserted_id)
    
    async def delete_lobby_by_id(
            self,
            *,
            lobby: LobbyInDB
    ) -> None:
        delete_result = await self.collection.delete_one({"_id": lobby.id})
        
        if delete_result.deleted_count != 1:
            raise HTTPException(status_code=404, detail=f"Lobby {lobby.id} not found")
    