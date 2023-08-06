from datetime import datetime
from typing import Type, Optional

import pytest
import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from pydantic import ValidationError
from starlette.datastructures import Secret

from async_asgi_testclient import TestClient

from fastapi import FastAPI, HTTPException, status

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from app.core.config import (
    SECRET_KEY, HOST_ADDRESS, JWT_ALGORITHM, JWT_AUDIENCE,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from app.db.repositories.users import UserRepository
from app.models.user import UserCreate, UserInDB

from app.services import auth_service, string_to_datetime


pytestmark = pytest.mark.asyncio


class TestUserRoutes:
    async def test_routes_exist(self, app: FastAPI, client: TestClient) -> None:
        new_user_data = {
            "email": "random@user.email",
            "username": "random_user",
            "password": "random_password"
        }
        res = await client.post(app.url_path_for("user:register"), json=new_user_data)
        assert res.status_code != HTTP_404_NOT_FOUND
        res = await client.post(app.url_path_for("user:login-email-and-password"), data=new_user_data)
        assert res.status_code != HTTP_404_NOT_FOUND
        res = await client.get(app.url_path_for("user:get-current-user"))
        assert res.status_code != HTTP_404_NOT_FOUND


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
        user_in_db = await user_repo.get_user_by_id(user_id=res.json()["id"])
        assert user_in_db is not None
        assert user_in_db.email == new_user_data["email"]
        assert user_in_db.username == new_user_data["username"]
        
        # check that the user returned in the response is equal to the user in the database
        created_user = res.json()
        # convert updated at string to datetime and remove access token
        created_user["updated_at"] = string_to_datetime(created_user["updated_at"])
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
            new_user_instance: UserCreate,
            test_user_instance: UserCreate,
            test_user: UserInDB
    ) -> None:
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


class TestUserLogin:
    async def test_user_login_with_email_and_receive_valid_token(
            self,
            app: FastAPI,
            client: TestClient,
            test_user_instance: UserCreate,
            test_user: UserInDB
    ) -> None:
        login_data = {
            "username": test_user_instance.email,
            "password": test_user_instance.password
        }
        res = await client.post(app.url_path_for("user:login-email-and-password"), form=login_data)
        assert res.status_code == status.HTTP_200_OK
        
        # check if the returned token has valid user data and type
        token = res.json().get("access_token")
        creds = jwt.decode(
            token,
            str(SECRET_KEY),
            issuer=HOST_ADDRESS,
            audience=JWT_AUDIENCE,
            algorithms=[JWT_ALGORITHM]
        )
        assert "username" in creds
        assert creds["username"] == test_user.username
        assert "sub" in creds
        assert creds["sub"] == test_user.email
        assert "token_type" in res.json()
        assert res.json().get("token_type") == "bearer"
    
    @pytest.mark.parametrize(
        "credential, wrong_value, status_code",
        (
                ("email", "wrong@email.com", 401),
                ("email", None, 401),
                ("email", "notemail", 401),
                ("password", "wrongpassword", 401),
                ("password", None, 401),
        ),
    )
    async def test_user_with_wrong_creds_doesnt_receive_token(
            self,
            app: FastAPI,
            client: TestClient,
            test_user_instance: UserCreate,
            test_user: UserInDB,
            credential: str,
            wrong_value: str,
            status_code: int,
    ) -> None:
        user_data = test_user_instance.model_dump()
        user_data[credential] = wrong_value
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"],
        }
        
        res = await client.post(app.url_path_for("user:login-email-and-password"), form=login_data)
        assert res.status_code == status_code
        assert "access_token" not in res.json()


class TestAuthToken:
    async def test_can_create_access_token_successfully(
            self,
            app: FastAPI,
            client: TestClient,
            test_user: UserInDB
    ) -> None:
        access_token = auth_service.create_access_token_for_user(
            user=test_user,
            secret_key=str(SECRET_KEY),
            issuer=HOST_ADDRESS,
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        
        creds = jwt.decode(
            access_token,
            str(SECRET_KEY),
            issuer=HOST_ADDRESS,
            audience=JWT_AUDIENCE,
            algorithms=[JWT_ALGORITHM]
        )
        assert creds.get("username") is not None
        assert creds["username"] == test_user.username
        assert creds["aud"] == JWT_AUDIENCE
    
    async def test_token_missing_user_is_invalid(
            self,
            app: FastAPI,
            client: TestClient
    ) -> None:
        access_token = auth_service.create_access_token_for_user(
            user=None,
            secret_key=str(SECRET_KEY),
            issuer=HOST_ADDRESS,
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        
        with pytest.raises(jwt.PyJWTError):
            jwt.decode(
                access_token,
                str(SECRET_KEY),
                issuer=HOST_ADDRESS,
                audience=JWT_AUDIENCE,
                algorithms=[JWT_ALGORITHM]
            )
    
    @pytest.mark.parametrize(
        "secret_key, jwt_issuer, jwt_audience, exception",
        (
                ("wrong-secret", HOST_ADDRESS, JWT_AUDIENCE, jwt.InvalidSignatureError),
                (None, HOST_ADDRESS, JWT_AUDIENCE, jwt.InvalidSignatureError),
                (SECRET_KEY, "other-site.io", JWT_AUDIENCE, jwt.InvalidIssuerError),
                (SECRET_KEY, None, JWT_AUDIENCE, ValidationError),
                (SECRET_KEY, HOST_ADDRESS, "othersite:auth", jwt.InvalidAudienceError),
                (SECRET_KEY, HOST_ADDRESS, None, ValidationError),
        ),
    )
    async def test_invalid_token_content_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            test_user: UserInDB,
            secret_key: Optional[str | Secret],
            jwt_issuer: Optional[str],
            jwt_audience: Optional[str],
            exception: Type[BaseException],
    ) -> None:
        with pytest.raises(exception):
            access_token = auth_service.create_access_token_for_user(
                user=test_user,
                secret_key=str(secret_key),
                issuer=jwt_issuer,
                audience=jwt_audience,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
            )
            
            jwt.decode(
                access_token,
                str(SECRET_KEY),
                issuer=HOST_ADDRESS,
                audience=JWT_AUDIENCE,
                algorithms=[JWT_ALGORITHM]
            )
    
    async def test_can_retrieve_username_from_token(
            self,
            app: FastAPI,
            client: TestClient,
            test_user: UserInDB
    ) -> None:
        token = auth_service.create_access_token_for_user(user=test_user, secret_key=str(SECRET_KEY))
        jwt_credentials = auth_service.get_username_from_token(
            token=token, secret_key=str(SECRET_KEY)
        )
        assert jwt_credentials.username == test_user.username
    
    @pytest.mark.parametrize(
        "secret, wrong_token",
        (
                (SECRET_KEY, "asdf"),
                (SECRET_KEY, ""),
                (SECRET_KEY, None),
                ("ABC123", "use correct token"),
        ),
    )
    async def test_error_when_token_or_secret_is_wrong(
            self,
            app: FastAPI,
            client: TestClient,
            test_user: UserInDB,
            secret: str | Secret,
            wrong_token: Optional[str],
    ) -> None:
        token = auth_service.create_access_token_for_user(user=test_user, secret_key=str(SECRET_KEY))
        
        if wrong_token == "use correct token":
            wrong_token = token
        
        with pytest.raises(HTTPException):
            username = auth_service.get_username_from_token(token=wrong_token, secret_key=str(secret))


class TestUserMe:
    async def test_authenticated_user_can_retrieve_own_data(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            test_user: UserInDB,
    ) -> None:
        res = await authorized_client.get(app.url_path_for("user:get-current-user"))
        assert res.status_code == HTTP_200_OK
        
        fetched_user = res.json()
        assert fetched_user["email"] == test_user.email
        assert fetched_user["username"] == test_user.username
        assert fetched_user["id"] == str(test_user.id)
    
    async def test_user_cannot_access_own_data_if_not_authenticated(
            self, app: FastAPI, client: TestClient, test_user: UserInDB,
    ) -> None:
        res = await client.get(app.url_path_for("user:get-current-user"))
        assert res.status_code == HTTP_401_UNAUTHORIZED
    
    @pytest.mark.parametrize(
        "jwt_prefix",
        (
                ("",), ("value",), ("Token",), ("JWT",), ("Swearer",),
        )
    )
    async def test_user_cannot_access_own_data_with_incorrect_jwt_prefix(
            self, app: FastAPI, client: TestClient, test_user: UserInDB, jwt_prefix: str,
    ) -> None:
        token = auth_service.create_access_token_for_user(user=test_user, secret_key=str(SECRET_KEY))
        res = await client.get(
            app.url_path_for("user:get-current-user"), headers={"Authorization": f"{jwt_prefix} {token}"}
        )
        assert res.status_code == HTTP_401_UNAUTHORIZED
