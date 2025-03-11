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
def token_generator() -> Callable[[UserModel], dict[str, str]]:
    def create_token(user: UserModel):
        token = create_access_token(data={"sub": user.username})
        return {"Authorization": f"Bearer {token}"}

    return create_token
