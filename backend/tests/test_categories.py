from typing import Dict, List

import pytest

from fastapi import FastAPI, status
from async_asgi_testclient import TestClient

from app.models.category import CategoryPublic, CategoryCreate

pytestmark = pytest.mark.asyncio


class TestCategoryRoutes:
    """
    Check each category route to ensure none return 404s
    """
    
    async def test_routes_exist(self, app: FastAPI, admin_client: TestClient, empty_category: CategoryPublic) -> None:
        category_id = empty_category.id
        
        res = await admin_client.get(app.url_path_for("category:get-all"))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await admin_client.get(app.url_path_for("category:get-by-id", category_id=category_id))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await admin_client.post(app.url_path_for("category:create"), json={})
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await admin_client.put(app.url_path_for("category:update-by-id", category_id=category_id))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await admin_client.delete(app.url_path_for("category:delete-by-id", category_id=category_id))
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestGetCategory:
    """
    Check list and get by categories
    """
    
    async def test_get_all_categories(
            self,
            app: FastAPI,
            admin_client: TestClient,
            category_list: List[CategoryPublic]
    ) -> None:
        res = await admin_client.get(
            app.url_path_for("category:get-all")
        )
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0
        
        dumped_category_list = [c.model_dump() for c in category_list]
        for fetched_category, created_category in zip(res.json(), dumped_category_list):
            assert fetched_category["id"] == created_category["id"]
            assert fetched_category["name"] == created_category["name"]
    
    async def test_get_category_by_id(
            self,
            app: FastAPI,
            admin_client: TestClient,
            empty_category: CategoryPublic
    ) -> None:
        res = await admin_client.get(
            app.url_path_for("category:get-by-id", category_id=empty_category.id)
        )
        assert res.status_code == status.HTTP_200_OK
        
        fetched_category = CategoryPublic.model_construct(**res.json())
        assert fetched_category == empty_category
    
    async def test_get_category_by_wrong_id_raises_not_found(
            self,
            app: FastAPI,
            admin_client: TestClient,
            random_object_id_str: str
    ):
        res = await admin_client.get(
            app.url_path_for("category:get-by-id", category_id=random_object_id_str)
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


class TestCreateCategory:
    """
    Check category creation with and without questions, with and without valid input
    """
    
    async def test_valid_input_crates_empty_category(
            self,
            app: FastAPI,
            admin_client: TestClient,
            new_empty_category_instance: CategoryCreate
    ) -> None:
        res = await admin_client.post(
            app.url_path_for("category:create"), json=new_empty_category_instance.model_dump()
        )
        assert res.status_code == status.HTTP_201_CREATED
        
        created_category = res.json()
        assert created_category["name"] == new_empty_category_instance.name
        assert created_category["questions"] == []
    
    async def test_valid_input_creates_populated_category(
            self,
            app: FastAPI,
            admin_client: TestClient,
            new_populated_category_instance: CategoryCreate
    ) -> None:
        res = await admin_client.post(
            app.url_path_for("category:create"), json=new_populated_category_instance.model_dump()
        )
        assert res.status_code == status.HTTP_201_CREATED
        
        created_category = res.json()
        assert created_category["name"] == new_populated_category_instance.name
        
        for fetched_question, created_question in zip(
                created_category["questions"],
                new_populated_category_instance.questions
        ):
            assert fetched_question["question"] == created_question.question
            assert fetched_question["answer"] == created_question.answer
            assert fetched_question["value"] == created_question.value
    
    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
                (None, 422),
                ({}, 422),
                ({"name": 1}, 422),
                ({"name": None}, 422),
                ({"name": ""}, 422),
                ({1: "name"}, 422),
                ({"questions": "question"}, 422),
                ({"name": "test", "questions": "question"}, 422),
                ({"name": "test", "questions": [
                    {"question": None, "answer": "answer", "value": 10}
                ]}, 422),
                ({"name": "test", "questions": [
                    {"question": "", "answer": "answer", "value": 10}
                ]}, 422),
                ({"name": "test", "questions": [
                    {"question": "question", "answer": None, "value": 10}
                ]}, 422),
                ({"name": "test", "questions": [
                    {"question": "question", "answer": "", "value": 10}
                ]}, 422),
                ({"name": "test", "questions": [
                    {"question": "question", "answer": "answer", "value": None}
                ]}, 422),
                ({"name": "test", "questions": [
                    {"question": "question", "answer": "answer", "value": -10}
                ]}, 422),
                ({"name": "test", "questions": [
                    {"question": "question", "answer": "answer", "value": 0}
                ]}, 422),
                ({"name": "test", "questions": [
                    {"question": "question", "answer": "answer", "value": 1.5}
                ]}, 422),
        ),
    )
    async def test_invalid_input_create_category_raises_error(
            self,
            app: FastAPI,
            admin_client: TestClient,
            invalid_payload: Dict[str | int, str | None | List[Dict[str, str | int | None]]] | None,
            status_code: int
    ):
        res = await admin_client.post(
            app.url_path_for("category:create"), json=invalid_payload
        )
        assert res.status_code == status_code
    
    async def test_unauthenticated_user_creates_category_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            new_empty_category_instance: CategoryCreate
    ) -> None:
        res = await client.post(
            app.url_path_for("category:create"), json=new_empty_category_instance.model_dump()
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_authenticated_non_admin_user_creates_category_raises_error(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            new_empty_category_instance: CategoryCreate
    ) -> None:
        res = await authorized_client.post(
            app.url_path_for("category:create"), json=new_empty_category_instance.model_dump()
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateCategory:
    """
    Check category update
    """
    
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
                (["name"], ["updated category name"]),
        ),
    )
    async def test_valid_input_updates_category(
            self,
            app: FastAPI,
            admin_client: TestClient,
            empty_category: CategoryPublic,
            attrs_to_change: List[str],
            values: List[str],
    ) -> None:
        category_update = {attrs_to_change[i]: values[i] for i in range(len(attrs_to_change))}
        res = await admin_client.put(
            app.url_path_for("category:update-by-id", category_id=empty_category.id),
            json=category_update
        )
        assert res.status_code == status.HTTP_200_OK
        
        fetched_category = res.json()
        assert fetched_category["id"] == empty_category.id
        
        # make sure that any attribute we updated has changed to the correct value
        for i in range(len(attrs_to_change)):
            assert fetched_category.get(attrs_to_change[i]) != getattr(empty_category, attrs_to_change[i])
            assert fetched_category.get(attrs_to_change[i]) == values[i]
        # make sure that no other attributes' values have changed
        for key, value in fetched_category.items():
            if key not in attrs_to_change:
                assert getattr(empty_category, key) == value
    
    @pytest.mark.parametrize(
        "payload, status_code",
        (
                ({"name": None}, 422),
                ({"name": ""}, 422),
                ({}, 422),
                ({"questions": [
                    {"question": "Test question", "answer": "Test answer", "value": 10}
                ]}, 422)
        ),
    )
    async def test_invalid_input_update_category_raises_error(
            self,
            app: FastAPI,
            admin_client: TestClient,
            empty_category: CategoryPublic,
            payload: Dict,
            status_code: int
    ) -> None:
        res = await admin_client.put(
            app.url_path_for("category:update-by-id", category_id=empty_category.id),
            json=payload
        )
        assert res.status_code == status_code
    
    async def test_update_category_with_wrong_id_raises_error(
            self,
            app: FastAPI,
            admin_client: TestClient,
            random_object_id_str: str
    ) -> None:
        res = await admin_client.put(
            app.url_path_for("category:update-by-id", category_id=random_object_id_str),
            json={"name": "Should throw an error"}
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_unauthenticated_user_updates_category_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            empty_category: CategoryPublic,
    ) -> None:
        res = await client.put(
            app.url_path_for("category:update-by-id", category_id=empty_category.id),
            json={"name": "anonymous user can't do update"}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_authenticated_non_admin_user_updates_category_raises_error(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            empty_category: CategoryPublic,
    ) -> None:
        res = await authorized_client.put(
            app.url_path_for("category:update-by-id", category_id=empty_category.id),
            json={"name": "anonymous user can't do update"}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteCategory:
    """
    Check category deletion
    """
    
    async def test_delete_valid_category(
            self,
            app: FastAPI,
            admin_client: TestClient,
            empty_category: CategoryPublic
    ) -> None:
        res = await admin_client.delete(
            app.url_path_for("category:delete-by-id", category_id=empty_category.id)
        )
        assert res.status_code == status.HTTP_204_NO_CONTENT
    
    async def test_delete_invalid_category_raises_error(
            self,
            app: FastAPI,
            admin_client: TestClient,
            random_object_id_str: str
    ) -> None:
        res = await admin_client.delete(
            app.url_path_for("category:delete-by-id", category_id=random_object_id_str)
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_unauthenticated_user_deletes_category_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            empty_category: CategoryPublic
    ) -> None:
        res = await client.delete(
            app.url_path_for("category:delete-by-id", category_id=empty_category.id)
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_authenticated_non_admin_user_deletes_category_raises_error(
            self,
            app: FastAPI,
            authorized_client: TestClient,
            empty_category: CategoryPublic
    ) -> None:
        res = await authorized_client.delete(
            app.url_path_for("category:delete-by-id", category_id=empty_category.id)
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
