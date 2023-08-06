from typing import List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories.base import BaseRepository
from app.models.core import PyObjectId
from app.models.player import PlayerPublic, PlayerCreate, PlayerUpdate

COLLECTION_CONFIG = {
    "name": "players",
    "index_fields": "name",
    "unique": False
}


class PlayerRepository(BaseRepository):
    """"
    All database actions associated with the Lobby resource
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db)
        self.collection = self.db.get_collection(COLLECTION_CONFIG["name"])
    
    async def list_players_in_lobby(
            self,
            *,
            lobby_id: str | PyObjectId,
            only_names: bool = False
    ) -> List[PlayerPublic] | List[str]:
        # select only player names of only_names enabled
        if only_names:
            player_records = await self.collection.find(
                {'lobby_id': lobby_id if isinstance(lobby_id, str) else str(lobby_id)},
                {"name": 1, "_id": 0}
            ).to_list(1000)
            return [pr["name"] for pr in player_records]
        
        player_records = await self.collection.find(
            {'lobby_id': lobby_id if isinstance(lobby_id, str) else str(lobby_id)}
        ).to_list(1000)
        
        return [PlayerPublic(**p) for p in player_records]
    
    async def get_player_by_name(
            self,
            *,
            lobby_id: str | PyObjectId,
            player_name: str
    ) -> PlayerPublic | None:
        fetched_player = await self.collection.find_one(
            {
                "name": player_name,
                "lobby_id": lobby_id if isinstance(lobby_id, str) else str(lobby_id)
            }
        )
        
        if fetched_player:
            return PlayerPublic(**fetched_player)
    
    async def create_player(
            self,
            *,
            player: PlayerCreate
    ) -> PlayerPublic:
        create_data = player.model_dump()
        encoded_new_player = jsonable_encoder(create_data)
        inserted_new_player = await self.collection.insert_one(encoded_new_player)
        
        if not inserted_new_player.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on player {inserted_new_player.inserted_id} could not be acknowledged"
            )
        
        return await self.get_player_by_name(
            lobby_id=player.lobby_id,
            player_name=player.name,
        )
    
    async def update_player_score(
            self,
            *,
            player: PlayerPublic,
            player_update: PlayerUpdate
    ) -> PlayerPublic:
        update_data = player_update.model_dump(exclude_unset=True, exclude_none=True)
        
        # If no changes are submitted, raise 304 error
        if not update_data:
            raise HTTPException(status_code=304, detail=f"Player {player.name} is not modified")
        
        updated_player = player.model_copy(update=update_data)
        encoded_updated_player = jsonable_encoder(updated_player)
        
        inserted_player = await self.collection.update_one(
            {"name": updated_player.name}, {"$set": encoded_updated_player}
        )
        
        if not inserted_player.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on player {updated_player.name} could not be acknowledged"
            )
        
        if (
                fetched_updated_player := await self.get_player_by_name(
                    lobby_id=player.lobby_id,
                    player_name=updated_player.name
                )
        ) is None:
            raise HTTPException(status_code=404, detail=f"Player {updated_player.name} not found")
        
        return fetched_updated_player
    
    async def delete_player_by_name(
            self,
            *,
            player: PlayerPublic
    ) -> None:
        delete_result = await self.collection.delete_one({"name": player.name})
        
        if delete_result.deleted_count != 1:
            raise HTTPException(status_code=404, detail=f"Player {player.name} not found")
    
    async def delete_players_for_lobby(
            self,
            *,
            lobby_id: str | PyObjectId
    ) -> int:
        deleted_records = await self.collection.delete_many(
            {'lobby_id': lobby_id if isinstance(lobby_id, str) else str(lobby_id)}
        )
        
        if not deleted_records.acknowledged:
            raise HTTPException(status_code=404, detail=f"Players for lobby {lobby_id} could not be deleted")
        
        return deleted_records.deleted_count
