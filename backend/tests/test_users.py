from datetime import datetime
from typing import List, Union, Type, Optional

import pytest
import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from pydantic import ValidationError
from starlette.datastructures import Secret

from async_asgi_testclient import TestClient
from fastapi import FastAPI

from fastapi import FastAPI, HTTPException, status

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_AUDIENCE, JWT_TOKEN_PREFIX, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.token import JWTMeta, JWTCreds, JWTPayload

from app.db.repositories.users import UserRepository
from app.models.user import UserCreate, UserInDB, UserPublic

from app.services import auth_service

pytestmark = pytest.mark.asyncio


# class TestUserRoutes:
#     async def test_routes_exist(self, app: FastAPI, client: TestClient) -> None:
#         new_user_data = {
#             "email": "random@user.email",
#             "username": "random_user",
#             "password": "random_password"
#         }
#         res = await client.post(app.url_path_for("user:register"), json=new_user_data)
#         assert res.status_code != HTTP_404_NOT_FOUND
#         res = await client.post(app.url_path_for("user:login-email-and-password"), data=new_user_data)
#         assert res.status_code != HTTP_404_NOT_FOUND
#         res = await client.get(app.url_path_for("user:get-current-user"))
#         assert res.status_code != HTTP_404_NOT_FOUND


class TestUserRegistration:
    async def test_user_register(
            self,
            app: FastAPI,
            client: TestClient,
            db: AsyncIOMotorDatabase,
            new_user_instance: UserCreate
    ) -> None:
        user_repo = UserRepository(db)
        new_user_data = new_user_instance.model_dump()

        # make sure user doesn't exist yet
        user_in_db = await user_repo.get_user_by_email(email=new_user_data["email"])
        assert user_in_db is None

        # send post request to create user and ensure it is successful
        res = await client.post(app.url_path_for("user:register"), json=new_user_data)
        assert res.status_code == HTTP_201_CREATED

        # ensure that the user now exists in the db
        # user_in_db = await user_repo.get_user_by_email(email=res.json()["email"])
        user_in_db = await user_repo.get_user_by_id(user_id=res.json()["id"])
        assert user_in_db is not None
        assert user_in_db.email == new_user_data["email"]
        assert user_in_db.username == new_user_data["username"]

        # check that the user returned in the response is equal to the user in the database
        created_user = res.json()
        # convert updated at string to datetime and remove access token
        created_user["updated_at"] = datetime.strptime(created_user["updated_at"], '%Y-%m-%dT%H:%M:%S.%f')
        created_user.pop("access_token")
        assert created_user == user_in_db.model_dump(exclude={"password", "salt"})
    
    @pytest.mark.parametrize(
        "attr, value, status_code",
        (
                ("email", "invalid_email@one@two.io", 422),
                ("password", "short", 422),
                ("username", "shakira@#$%^<>", 422),
                ("username", "ab", 422),
        ),
    )
    async def test_user_registration_fails_when_credentials_are_badly_formatted(
            self,
            app: FastAPI,
            client: TestClient,
            new_user_instance: UserCreate,
            attr: str,
            value: str,
            status_code: int,
    ) -> None:
        new_user = new_user_instance.model_dump()
        new_user[attr] = value
        res = await client.post(app.url_path_for("user:register"), json=new_user)
        assert res.status_code == status_code
    
    async def test_user_registration_fails_when_credentials_are_taken(
            self,
            app: FastAPI,
            client: TestClient,
            db: AsyncIOMotorDatabase,
            new_user_instance: UserCreate,
            test_user_instance: UserCreate,
    ) -> None:
        # register test user
        user_repo = UserRepository(db)
        test_user_in_db = await user_repo.register_new_user(new_user=test_user_instance)
        
        # repeat email
        new_user = new_user_instance.model_dump()
        new_user["email"] = getattr(test_user_instance, "email")
        res = await client.post(app.url_path_for("user:register"), json=new_user)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        
        # repeat username
        new_user = new_user_instance.model_dump()
        new_user["username"] = getattr(test_user_instance, "username")
        res = await client.post(app.url_path_for("user:register"), json=new_user)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
    
    async def test_users_saved_password_is_hashed_and_has_salt(
            self,
            app: FastAPI,
            client: TestClient,
            db: AsyncIOMotorDatabase,
            new_user_instance: UserCreate,
    ) -> None:
        user_repo = UserRepository(db)
        new_user = new_user_instance.model_dump()

        # send post request to create user and ensure it is successful
        res = await client.post(app.url_path_for("user:register"), json=new_user)
        assert res.status_code == HTTP_201_CREATED

        # ensure that the users password is hashed in the db
        # and that we can verify it using our auth service
        user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is not None
        assert user_in_db.salt is not None and user_in_db.salt != "123"
        assert user_in_db.password != new_user["password"]
        assert auth_service.verify_password(
            password=new_user["password"], salt=user_in_db.salt, hashed_pw=user_in_db.password,
        )
