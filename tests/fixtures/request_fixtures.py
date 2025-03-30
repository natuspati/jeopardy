from typing import Callable

import pytest

from jlib.utils.auth import create_access_token
from models.user import UserModel


@pytest.fixture
def pagination() -> dict[str, int]:
    return {
        "offset": 0,
        "limit": 10,
    }


@pytest.fixture
def auth_query_param() -> Callable[[UserModel], dict[str, str]]:
    def create_auth_query_param(user: UserModel):
        return {"token": create_access_token(data={"sub": user.username})}

    return create_auth_query_param


@pytest.fixture
def auth_header() -> Callable[[UserModel], dict[str, str]]:
    def create_auth_header(user: UserModel):
        token = create_access_token(data={"sub": user.username})
        return {"Authorization": f"Bearer {token}"}

    return create_auth_header
