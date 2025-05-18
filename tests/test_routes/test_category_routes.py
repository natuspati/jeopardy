import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

from jlib.db import DBManager
from jlib.schemas.prompt import PromptPriorityUpdateSchema, PromptShowSchema
from models.category import CategoryModel
from models.prompt import PromptModel
from models.user import UserModel


def test_get_categories(
    client: TestClient,
    categories: list[CategoryModel],
    pagination: dict[str, int],
):
    resp = client.get("/api/v1/category", params=pagination)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["items"]) == len(categories)


def test_get_category(
    client: TestClient,
    categories: list[CategoryModel],
    prompts: list[PromptModel],
):
    # success
    category = categories[0]
    selected_prompts = [p for p in prompts if p.category_id == category.id]
    resp = client.get(f"/api/v1/category/{category.id}")
    assert resp.status_code == status.HTTP_200_OK

    fetched_category = resp.json()
    fetched_prompts = fetched_category.pop("prompts")
    assert len(fetched_prompts) == len(selected_prompts)
    for field, value in fetched_category.items():
        assert value == getattr(category, field)
    selected_prompts_as_dict = [
        PromptShowSchema.model_validate(p, from_attributes=True).model_dump()
        for p in selected_prompts
    ]
    for fetched_prompt in fetched_prompts:
        assert fetched_prompt in selected_prompts_as_dict

    # not found
    non_existing_category_id = categories[-1].id + 1
    resp = client.get(f"/api/v1/category/{non_existing_category_id}")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_create_category(
    client: TestClient,
    user: UserModel,
    categories_data: list[dict],
    auth_header,
    db_manager: DBManager,
):
    # success
    category_to_create = next(
        (cat for cat in categories_data if cat["owner_id"] == user.id),
        None,
    )
    if not category_to_create:
        pytest.fail("No category to create with provided user")
    user_id = category_to_create.pop("owner_id")
    resp = client.post(
        "/api/v1/category",
        json=category_to_create,
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_201_CREATED
    async with db_manager.session() as session:
        category_in_db = await session.scalar(
            select(CategoryModel).where(CategoryModel.id == resp.json()["id"]),
        )
        assert category_in_db.owner_id == user_id
        assert category_in_db.name == category_to_create["name"]

    # unauthorized
    resp = client.post("/api/v1/category", json=category_to_create)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # category already exists
    resp = client.post(
        "/api/v1/category",
        json=category_to_create,
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_409_CONFLICT


async def test_update_category(
    client: TestClient,
    users: list[UserModel],
    categories: list[CategoryModel],
    prompts: list[PromptModel],
    auth_header,
    db_manager: DBManager,
):
    user, wrong_user = users[0], users[1]
    category = next((cat for cat in categories if cat.owner_id == user.id), None)
    if not category:
        pytest.fail("No category to delete with provided user")
    selected_prompts = [p for p in prompts if p.category_id == category.id]

    # success, new name
    new_name = "new name"
    resp = client.patch(
        f"/api/v1/category/{category.id}",
        json={"name": new_name},
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_200_OK
    async with db_manager.session() as session:
        category_in_db = await session.scalar(
            select(CategoryModel).where(CategoryModel.id == category.id),
        )
        assert category_in_db.name == new_name

    # success, new prompt priority
    total = len(selected_prompts)
    updated_prompts = []
    for selected_prompt in selected_prompts:
        prompt = PromptPriorityUpdateSchema.model_validate(
            selected_prompt,
            from_attributes=True,
        )
        prompt.default_priority = total - prompt.default_priority + 1
        updated_prompts.append(prompt.model_dump())

    resp = client.patch(
        f"/api/v1/category/{category.id}",
        json={"prompts": updated_prompts},
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_200_OK
    fetched_prompts = resp.json()["prompts"]
    for fetched_prompt in fetched_prompts:
        updated_prompt = next(
            (p for p in updated_prompts if p["id"] == fetched_prompt["id"]),
            None,
        )
        assert fetched_prompt["default_priority"] == updated_prompt["default_priority"]

    # wrong user tries to change category
    resp = client.patch(
        f"/api/v1/category/{category.id}",
        json={"name": "new name"},
        headers=auth_header(wrong_user),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # wrong number of prompts to update priority
    resp = client.patch(
        f"/api/v1/category/{category.id}",
        json={"prompts": updated_prompts[:-1]},
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # empty data
    resp = client.patch(
        f"/api/v1/category/{category.id}",
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_delete_category(
    client: TestClient,
    users: list[UserModel],
    categories: list[CategoryModel],
    auth_header,
    db_manager: DBManager,
):
    user, wrong_user = users[0], users[1]
    category = next((cat for cat in categories if cat.owner_id == user.id), None)
    if not category:
        pytest.fail("No category to delete with provided user")

    # wrong user tries to delete
    resp = client.delete(
        f"/api/v1/category/{category.id}",
        headers=auth_header(wrong_user),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # success
    resp = client.delete(
        f"/api/v1/category/{category.id}",
        headers=auth_header(user),
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    async with db_manager.session() as session:
        category_in_db = await session.scalar(
            select(CategoryModel).where(CategoryModel.id == category.id),
        )
        assert not category_in_db
