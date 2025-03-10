import pytest
from fastapi import status
from fastapi.testclient import TestClient

from jlib.utils.auth import decode_token
from models.user import UserModel


def test_login_route(
    client: TestClient, users: list[UserModel], users_data: list[dict]
):
    user_model = next((u for u in users if not u.deleted), None)
    user = next((u for u in users_data if u["username"] == user_model.username), None)
    if not user_model or not user:
        pytest.fail("No user found")
    resp = client.post(
        "/api/v1/user/token",
        data={
            "username": user_model.username,
            "password": user["password"],
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED
    created_token = resp.json().get("access_token")
    assert created_token
    decoded_token = decode_token(created_token)
    assert decoded_token.username == user_model.username
