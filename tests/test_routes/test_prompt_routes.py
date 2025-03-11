from typing import Callable

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from models.category import CategoryModel
from models.prompt import PromptModel
from models.user import UserModel


def test_create_prompt(
    client: TestClient,
    users: list[UserModel],
    categories: list[CategoryModel],
    token_generator: Callable[[UserModel], dict[str, str]],
):
    user, wrong_user = users[0], users[1]

    category = next((cat for cat in categories if cat.owner_id == user.id), None)
    if not category:
        pytest.fail("No category to delete with provided user")

    # success
    new_prompt = {
        "question": "new question",
        "question_type": "text",
        "answer": "new answer",
        "answer_type": "text",
        "default_priority": 1,
    }
    resp = client.post(
        f"/api/v1/category/{category.id}/prompt",
        json=new_prompt,
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_201_CREATED
    created_prompt = resp.json()
    created_prompt.pop("id")
    assert category.id == created_prompt.pop("category_id")
    assert created_prompt == new_prompt

    # prompt with the same priority already exists
    resp = client.post(
        f"/api/v1/category/{category.id}/prompt",
        json=new_prompt,
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_409_CONFLICT

    # category of the prompt does not exist
    non_existing_category_id = max((cat.id for cat in categories)) + 1
    resp = client.post(
        f"/api/v1/category/{non_existing_category_id}/prompt",
        json=new_prompt,
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    # user adds prompt to category they do not own
    resp = client.post(
        f"/api/v1/category/{category.id}/prompt",
        json=new_prompt,
        headers=token_generator(wrong_user),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_update_prompt(
    client: TestClient,
    users: list[UserModel],
    categories: list[CategoryModel],
    prompts: list[PromptModel],
    token_generator: Callable[[UserModel], dict[str, str]],
):
    user, wrong_user = users[0], users[1]
    category = next((cat for cat in categories if cat.owner_id == user.id), None)
    if not category:
        pytest.fail("No category to delete with provided user")
    prompt = next((p for p in prompts if p.category_id == category.id), None)
    if not prompt:
        pytest.fail("No prompt to update")

    # success
    new_prompt = {
        "question": "new question",
        "answer": "answer.png",
        "answer_type": "image",
    }
    resp = client.patch(
        f"/api/v1/category/{category.id}/prompt/{prompt.id}",
        json=new_prompt,
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_200_OK
    fetched_prompt: dict = resp.json()
    assert fetched_prompt.pop("id") == prompt.id
    assert fetched_prompt.pop("category_id") == prompt.category_id
    assert fetched_prompt.pop("default_priority") == prompt.default_priority
    for field, value in new_prompt.items():
        assert fetched_prompt[field] == value

    # empty data
    resp = client.patch(
        f"/api/v1/category/{category.id}/prompt/{prompt.id}",
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # wrong user trying to update prompt
    resp = client.patch(
        f"/api/v1/category/{category.id}/prompt/{prompt.id}",
        json=new_prompt,
        headers=token_generator(wrong_user),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # wrong category id
    wrong_category = next(
        (
            cat
            for cat in categories
            if cat.owner_id == user.id and cat.id != category.id
        ),
        None,
    )
    resp = client.patch(
        f"/api/v1/category/{wrong_category.id}/prompt/{prompt.id}",
        json=new_prompt,
        headers=token_generator(user),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
