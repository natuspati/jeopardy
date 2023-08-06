from typing import List, Dict

import pytest

from fastapi import FastAPI, status
from async_asgi_testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.repositories.players import PlayerRepository
from app.models.lobby import LobbyPublic
from app.models.player import PlayerPublic
from app.models.user import UserInDB

from app.services import datetime_to_string

pytestmark = pytest.mark.asyncio


class TestLobbyRoutes:
    """
    Check each lobby route to ensure none return 404s
    """

    async def test_routes_exist(
            self, app: FastAPI, client: TestClient, empty_lobby: LobbyPublic
    ) -> None:
        res = await client.get(app.url_path_for("lobby:get-active"))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.get(app.url_path_for("lobby:get-by-id", lobby_id=empty_lobby.id))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.post(app.url_path_for("lobby:create"), json={})
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.delete(app.url_path_for("lobby:delete-by-id", lobby_id=empty_lobby.id))
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestGetLobby:
    """
    Check list and get lobbies
    """

    async def test_get_active_lobbies(
            self,
            app: FastAPI,
            client: TestClient,
            active_lobby_list: List[LobbyPublic]
    ) -> None:
        res = await client.get(app.url_path_for("lobby:get-active"))
        fetched_lobbies = res.json()
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(fetched_lobbies, list)
        assert len(fetched_lobbies) > 0

        for fetched_lobby, created_lobby in zip(fetched_lobbies, active_lobby_list):
            assert fetched_lobby["id"] == str(getattr(created_lobby, "id"))
            assert fetched_lobby["owner"] == getattr(created_lobby, "owner")
            assert fetched_lobby["active"] == getattr(created_lobby, "active")

    async def test_get_lobby_by_id(
            self,
            app: FastAPI,
            client: TestClient,
            empty_lobby: LobbyPublic
    ) -> None:
        res = await client.get(app.url_path_for("lobby:get-by-id", lobby_id=empty_lobby.id))
        assert res.status_code == status.HTTP_200_OK

        dumped_empty_lobby = empty_lobby.model_dump()
        dumped_empty_lobby["updated_at"] = datetime_to_string(dumped_empty_lobby["updated_at"])
        assert res.json() == dumped_empty_lobby

    async def test_get_lobby_by_wrong_id_raises_not_found(
            self,
            app: FastAPI,
            client: TestClient,
            random_object_id_str: str
    ) -> None:
        res = await client.get(app.url_path_for("lobby:get-by-id", lobby_id=random_object_id_str))
        assert res.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_inactive_lobby_by_id_raises_not_found(
            self,
            app: FastAPI,
            client: TestClient,
            inactive_lobby: LobbyPublic
    ) -> None:
        res = await client.get(app.url_path_for("lobby:get-by-id", lobby_id=inactive_lobby.id))
        assert res.status_code == status.HTTP_404_NOT_FOUND


class TestCreateLobby:
    """
    Check Lobby creation
    """
    async def test_authenticated_user_creates_lobby(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            test_user: UserInDB
    ) -> None:
        res = await authorized_client.post(app.url_path_for("lobby:create"))
        assert res.status_code == status.HTTP_201_CREATED

        created_lobby = res.json()
        assert created_lobby["owner"] == test_user.username
        assert created_lobby["active"]

    async def test_unauthenticated_user_creates_lobby_raises_error(
            self,
            app: FastAPI,
            client: TestClient
    ) -> None:
        res = await client.post(app.url_path_for("lobby:create"))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteLobby:
    """
    Check only lobby owner can delete the lobby
    """

    async def test_lobby_owner_deletes_empty_lobby(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            empty_lobby: LobbyPublic
    ) -> None:
        res = await authorized_client.delete(
            app.url_path_for("lobby:delete-by-id", lobby_id=empty_lobby.id)
        )
        assert res.status_code == status.HTTP_204_NO_CONTENT

    async def test_populated_lobby_delete_removes_associated_players(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            populated_lobby: Dict[str, LobbyPublic | UserInDB | List[PlayerPublic]],
            db: AsyncIOMotorDatabase
    ) -> None:
        res = await authorized_client.delete(
            app.url_path_for("lobby:delete-by-id", lobby_id=populated_lobby["lobby"].id)
        )
        assert res.status_code == status.HTTP_204_NO_CONTENT

        player_repo = PlayerRepository(db)
        assert await player_repo.list_players_in_lobby(lobby_id=populated_lobby["lobby"].id) == []

    async def test_delete_lobby_by_wrong_id_raises_error(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            random_object_id_str
    ) -> None:
        res = await authorized_client.delete(
            app.url_path_for("lobby:delete-by-id", lobby_id=random_object_id_str)
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    async def test_other_users_delete_lobby_raises_error(
            self,
            app: FastAPI,
            admin_client: TestClient,
            empty_lobby: LobbyPublic
    ) -> None:
        res = await admin_client.delete(
            app.url_path_for("lobby:delete-by-id", lobby_id=empty_lobby.id)
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    async def test_non_authenticated_user_delete_lobby_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            empty_lobby: LobbyPublic
    ) -> None:
        res = await client.delete(
            app.url_path_for("lobby:delete-by-id", lobby_id=empty_lobby.id)
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
