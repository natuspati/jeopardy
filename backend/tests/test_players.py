from typing import Dict, List, Callable, Optional

import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI
from starlette import status

from app.models.lobby import LobbyPublic
from app.models.player import PlayerPublic
from app.models.user import UserInDB

pytestmark = pytest.mark.asyncio


class TestPlayerRoutes:
    """
    Check each player route to ensure none return 404s
    """
    
    async def test_routes_exist(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        lobby = populated_lobby["lobby"]
        player_one = populated_lobby["players"][0]
        
        res = await authorized_client.get(
            app.url_path_for("player:get-players-in-lobby", lobby_id=lobby.id)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await authorized_client.get(
            app.url_path_for("player:get-by-name", lobby_id=lobby.id, player_name=player_one.name)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await authorized_client.post(
            app.url_path_for("player:add-to-lobby", lobby_id=lobby.id)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await authorized_client.put(
            app.url_path_for("player:update-score-by-name", lobby_id=lobby.id, player_name=player_one.name),
            json={"score": 1}
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await authorized_client.delete(
            app.url_path_for("player:delete-by-name", lobby_id=lobby.id, player_name=player_one.name)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestGetPlayer:
    """
    Check list and get players in a lobby
    """
    
    async def test_lobby_owner_can_get_players_in_lobby(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        res = await authorized_client.get(
            app.url_path_for("player:get-players-in-lobby", lobby_id=populated_lobby["lobby"].id)
        )
        assert res.status_code == status.HTTP_200_OK
        
        fetched_players = res.json()
        assert isinstance(fetched_players, list)
        assert len(fetched_players) > 0
        
        for fetched_player, created_player in zip(fetched_players, populated_lobby["players"]):
            for attr in fetched_player.keys():
                assert fetched_player[attr] == getattr(created_player, attr)
    
    async def test_user_in_lobby_can_get_players_in_lobby(
            self,
            app: FastAPI,
            client: TestClient,
            user_one: UserInDB,
            authenticate_client: Callable,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        authorized_client = authenticate_client(client=client, user=user_one)
        res = await authorized_client.get(
            app.url_path_for("player:get-players-in-lobby", lobby_id=populated_lobby["lobby"].id)
        )
        assert res.status_code == status.HTTP_200_OK
        
        fetched_players = res.json()
        assert isinstance(fetched_players, list)
        assert len(fetched_players) > 0
        
        for fetched_player, created_player in zip(fetched_players, populated_lobby["players"]):
            for attr in fetched_player.keys():
                assert fetched_player[attr] == getattr(created_player, attr)
    
    async def test_user_not_in_lobby_cannot_get_players_in_lobby(
            self,
            app: FastAPI,
            admin_client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        res = await admin_client.get(
            app.url_path_for("player:get-players-in-lobby", lobby_id=populated_lobby["lobby"].id)
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN
    
    async def test_unauthenticated_user_cannot_get_players_in_lobby(
            self,
            app: FastAPI,
            client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        res = await client.get(
            app.url_path_for("player:get-players-in-lobby", lobby_id=populated_lobby["lobby"].id)
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_lobby_owner_can_get_player_by_name(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        player_one = populated_lobby["players"][0]
        res = await authorized_client.get(
            app.url_path_for(
                "player:get-by-name",
                lobby_id=populated_lobby["lobby"].id,
                player_name=player_one.name
            )
        )
        assert res.status_code == status.HTTP_200_OK
        
        fetched_player = res.json()
        for attr in fetched_player.keys():
            assert fetched_player[attr] == getattr(player_one, attr)
    
    async def test_user_in_lobby_can_get_player_by_name(
            self,
            app: FastAPI,
            client: TestClient,
            user_two: UserInDB,
            authenticate_client: Callable,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        authorized_client = authenticate_client(client=client, user=user_two)
        player_one = populated_lobby["players"][0]
        res = await authorized_client.get(
            app.url_path_for(
                "player:get-by-name",
                lobby_id=populated_lobby["lobby"].id,
                player_name=player_one.name
            )
        )
        assert res.status_code == status.HTTP_200_OK
        
        fetched_player = res.json()
        for attr in fetched_player.keys():
            assert fetched_player[attr] == getattr(player_one, attr)
    
    async def test_user_get_player_in_wrong_lobby_raises_error(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            empty_lobby: LobbyPublic,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        res = await authorized_client.get(
            app.url_path_for(
                "player:get-by-name",
                lobby_id=empty_lobby.id,
                player_name=populated_lobby["players"][0].name
            )
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_user_not_in_lobby_cannot_get_player_by_name(
            self,
            app: FastAPI,
            admin_client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        player_one = populated_lobby["players"][0]
        res = await admin_client.get(
            app.url_path_for(
                "player:get-by-name",
                lobby_id=populated_lobby["lobby"].id,
                player_name=player_one.name
            )
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN
    
    async def test_unauthenticated_user_cannot_get_player_by_name(
            self,
            app: FastAPI,
            client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]]
    ) -> None:
        player_one = populated_lobby["players"][0]
        res = await client.get(
            app.url_path_for(
                "player:get-by-name",
                lobby_id=populated_lobby["lobby"].id,
                player_name=player_one.name
            )
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreatePlayer:
    """
    Check player creation
    """
    
    async def test_user_creates_new_player(
            self,
            app: FastAPI,
            client: TestClient,
            empty_lobby: LobbyPublic,
            random_generated_user: UserInDB,
            authenticate_client: Callable
    ) -> None:
        authorized_client = authenticate_client(client=client, user=random_generated_user)
        res = await authorized_client.post(app.url_path_for("player:add-to-lobby", lobby_id=empty_lobby.id))
        
        assert res.status_code == status.HTTP_201_CREATED
        
        created_player = res.json()
        assert created_player["name"] == random_generated_user.username
        assert created_player["lobby_id"] == str(empty_lobby.id)
        assert created_player["score"] == 0
    
    async def test_unauthenticated_user_creates_player_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            empty_lobby: LobbyPublic
    ) -> None:
        res = await client.post(app.url_path_for("player:add-to-lobby", lobby_id=empty_lobby.id))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdatePlayer:
    """
    Check player update
    """
    
    async def test_user_owning_player_can_update(
            self,
            app: FastAPI,
            client: TestClient,
            user_one: UserInDB,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]],
            authenticate_client: Callable
    ) -> None:
        authorized_client = authenticate_client(client=client, user=user_one)
        lobby = populated_lobby["lobby"]
        player_one = populated_lobby["players"][0]
        
        res = await authorized_client.put(
            app.url_path_for(
                "player:update-score-by-name",
                lobby_id=lobby.id,
                player_name=player_one.name
            ),
            json={"score": 1}
        )
        assert res.status_code == status.HTTP_200_OK
        
        fetched_player = res.json()
        assert fetched_player["name"] == player_one.name
        assert fetched_player["lobby_id"] == player_one.lobby_id
        assert fetched_player["score"] == 1
    
    @pytest.mark.parametrize(
        "payload, status_code",
        (
                ({"score": None}, 422),
                ({"score": 0.5}, 422),
                ({}, 422),
                (None, 422),
        ),
    )
    async def test_user_updates_with_invalid_input_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            user_one: UserInDB,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]],
            authenticate_client: Callable,
            payload: Optional[Dict[str, Optional[float]]],
            status_code: int
    ) -> None:
        authorized_client = authenticate_client(client=client, user=user_one)
        lobby = populated_lobby["lobby"]
        player_one = populated_lobby["players"][0]
        
        res = await authorized_client.put(
            app.url_path_for(
                "player:update-score-by-name",
                lobby_id=lobby.id,
                player_name=player_one.name
            ),
            json=payload
        )
        assert res.status_code == status_code
    
    async def test_users_not_owning_player_update_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            user_two: UserInDB,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]],
            authenticate_client: Callable,
    ) -> None:
        authorized_client = authenticate_client(client=client, user=user_two)
        lobby = populated_lobby["lobby"]
        player_one = populated_lobby["players"][0]
        
        res = await authorized_client.put(
            app.url_path_for(
                "player:update-score-by-name",
                lobby_id=lobby.id,
                player_name=player_one.name
            ),
            json={"score": 1}
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN
    
    async def test_unauthenticated_user_updates_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]],
    ) -> None:
        lobby = populated_lobby["lobby"]
        player_one = populated_lobby["players"][0]
        
        res = await client.put(
            app.url_path_for(
                "player:update-score-by-name",
                lobby_id=lobby.id,
                player_name=player_one.name
            ),
            json={"score": 1}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_user_update_player_in_wrong_lobby_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            user_one: UserInDB,
            empty_lobby: LobbyPublic,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]],
            authenticate_client: Callable
    ) -> None:
        authorized_client = authenticate_client(client=client, user=user_one)
        player_one = populated_lobby["players"][0]
        
        res = await authorized_client.put(
            app.url_path_for(
                "player:update-score-by-name",
                lobby_id=empty_lobby.id,
                player_name=player_one.name
            ),
            json={"score": 1}
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
