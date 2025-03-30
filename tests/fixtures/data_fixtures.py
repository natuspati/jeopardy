import uuid

import pytest

from jlib.enums import LobbyMemberTypeEnum, LobbyStateEnum


@pytest.fixture
def users_data() -> list[dict]:
    return [
        {
            "username": "user_1",
            "password": "password",
            "deleted": False,
        },
        {
            "username": "user_2",
            "password": "password",
            "deleted": False,
        },
        {
            "username": "user_3",
            "password": "password",
            "deleted": False,
        },
    ]


@pytest.fixture
def categories_data() -> list[dict]:
    return [
        {
            "name": "category_1",
            "owner_id": 1,
        },
        {
            "name": "category_2",
            "owner_id": 1,
        },
        {
            "name": "category_3",
            "owner_id": 2,
        },
    ]


@pytest.fixture
def prompts_data() -> list[dict]:
    return [
        {
            "question": "question_1",
            "question_type": 1,
            "answer": "answer_1",
            "answer_type": 1,
            "default_priority": 1,
            "category_id": 1,
        },
        {
            "question": "question_2",
            "question_type": 1,
            "answer": "answer_2",
            "answer_type": 1,
            "default_priority": 2,
            "category_id": 1,
        },
        {
            "question": "question_3",
            "question_type": 1,
            "answer": "answer_3",
            "answer_type": 1,
            "default_priority": 3,
            "category_id": 1,
        },
        {
            "question": "question_1",
            "question_type": 1,
            "answer": "answer_1",
            "answer_type": 1,
            "default_priority": 1,
            "category_id": 2,
        },
        {
            "question": "question_2",
            "question_type": 1,
            "answer": "answer_2",
            "answer_type": 1,
            "default_priority": 2,
            "category_id": 2,
        },
        {
            "question": "question_3",
            "question_type": 1,
            "answer": "answer_3",
            "answer_type": 1,
            "default_priority": 3,
            "category_id": 2,
        },
    ]


@pytest.fixture
def unpopulated_presets_data() -> list[dict]:
    return [
        {
            "name": "preset_1",
            "owner_id": 1,
        },
        {
            "name": "preset_2",
            "owner_id": 2,
        },
    ]


@pytest.fixture
def presets_data() -> list[dict]:
    return [
        {
            "preset_id": 1,
            "category_id": 1,
        },
        {
            "preset_id": 1,
            "category_id": 2,
        },
        {
            "preset_id": 2,
            "category_id": 1,
        },
        {
            "preset_id": 2,
            "category_id": 2,
        },
    ]


@pytest.fixture
def lobby_data() -> dict:
    lobby_id = uuid.uuid4()
    return {
        "id": lobby_id,
        "state": LobbyStateEnum.CREATE,
        "players": [
            {
                "username": "user_1",
                "lobby_id": lobby_id,
                "score": None,
                "type": LobbyMemberTypeEnum.LEAD,
            },
            {
                "username": "user_2",
                "lobby_id": lobby_id,
                "score": None,
                "type": LobbyMemberTypeEnum.PLAYER,
            },
            {
                "username": "user_3",
                "lobby_id": lobby_id,
                "score": None,
                "type": LobbyMemberTypeEnum.PLAYER,
            },
        ],
    }
