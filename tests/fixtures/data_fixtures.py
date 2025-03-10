import pytest


@pytest.fixture
def users_data() -> list[dict]:
    return [
        {
            "username": "user_1",
            "password": "password",
            "deleted": False,
        },
        {
            "username": "deleted_user",
            "password": "password",
            "deleted": True,
        },
    ]
