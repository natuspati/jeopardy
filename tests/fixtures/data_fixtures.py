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
