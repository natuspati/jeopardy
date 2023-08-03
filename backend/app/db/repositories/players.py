from typing import List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.db.repositories.base import BaseRepository
from app.models.core import PyObjectId
from app.models.lobby import LobbyInDB
from app.models.player import PlayerPublic, PlayerCreate, PlayerUpdate


class PlayerRepository(BaseRepository):
    """"
    All database actions associated with the Lobby resource
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = self.db.get_collection("players")
    
    async def list_players_for_lobby(
            self,
            *,
            lobby_id: str | PyObjectId
    ) -> List[PlayerPublic]:
        player_records = await self.collection.find(
            {'lobby_id': lobby_id if isinstance(lobby_id, str) else str(lobby_id)}
        ).to_list(1000)
        
        return [PlayerPublic(**p) for p in player_records]
    
    async def get_player_by_id(
            self,
            *,
            lobby_id: str | PyObjectId,
            player_id: str | PyObjectId
    ) -> PlayerPublic | None:
        fetched_player = await self.collection.find_one(
            {
                "_id": PyObjectId(player_id) if isinstance(player_id, str) else player_id,
                "lobby_id": lobby_id if isinstance(lobby_id, str) else str(lobby_id)
            }
        )
        
        if fetched_player:
            return PlayerPublic(**fetched_player)
    
    async def create_player(
            self,
            *,
            player: PlayerCreate,
            lobby: LobbyInDB
    ) -> PlayerPublic:
        create_data = player.model_dump()
        encoded_new_player = jsonable_encoder(create_data)
        inserted_new_player = await self.collection.insert_one(encoded_new_player)
        
        if not inserted_new_player.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on player {inserted_new_player.inserted_id} could not be acknowledged"
            )
        
        return await self.get_player_by_id(
            lobby_id=lobby.id,
            player_id=inserted_new_player.inserted_id,
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
            raise HTTPException(status_code=304, detail=f"Player {player.id} is not modified")
        
        updated_player = player.model_copy(update=update_data)
        encoded_updated_player = jsonable_encoder(updated_player)
        
        inserted_player = await self.collection.update_one(
            {"_id": updated_player.id}, {"$set": encoded_updated_player}
        )
        
        if not inserted_player.acknowledged:
            raise HTTPException(
                status_code=400,
                detail=f"Operation on player {player.id} could not be acknowledged"
            )
        
        if (
                fetched_updated_player := await self.get_player_by_id(
                    lobby_id=player.lobby_id,
                    player_id=player.id
                )
        ) is None:
            raise HTTPException(status_code=404, detail=f"Player {player.id} not found")
        
        return fetched_updated_player
    
    async def delete_player_by_id(
            self,
            *,
            player: PlayerPublic
    ) -> None:
        delete_result = await self.collection.delete_one({"_id": player.id})
        
        if delete_result.deleted_count != 1:
            raise HTTPException(status_code=404, detail=f"Player {player.id} not found")
    
    async def delete_players_for_lobby(
            self,
            *,
            lobby_id: str | PyObjectId
    ) -> int:
        deleted_records = await self.collection.delete_many(
            {'category_id': lobby_id if isinstance(lobby_id, str) else str(lobby_id)}
        )
        
        if not deleted_records.acknowledged:
            raise HTTPException(status_code=404, detail=f"Players for lobby {lobby_id} not deleted")
        
        return deleted_records.deleted_count
