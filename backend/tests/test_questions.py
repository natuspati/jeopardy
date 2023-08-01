from typing import Callable, List, Dict

import pytest

from fastapi import FastAPI, status
from async_asgi_testclient import TestClient

from app.models.category import CategoryPublic

pytestmark = pytest.mark.asyncio


class TestQuestionRoutes:
    """
    Check question routes to ensure none return 404s
    """

    async def test_routes(
            self,
            app: FastAPI,
            client: TestClient,
            category_with_one_question: CategoryPublic
    ) -> None:
        category_id = category_with_one_question.id
        question_id = category_with_one_question.questions[0]["id"]

        res = await client.get(app.url_path_for("question:get-list-for-category", category_id=category_id))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.get(
            app.url_path_for("question:get-by-id", category_id=category_id, question_id=question_id),
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.post(app.url_path_for("question:create", category_id=category_id))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.put(
            app.url_path_for("question:update-by-id", category_id=category_id, question_id=question_id)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.delete(
            app.url_path_for("question:delete-by-id", category_id=category_id, question_id=question_id)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestGetQuestions:
    """
    Check list and get by id questions for a category
    """

    async def test_list_questions_for_category(
            self,
            app: FastAPI,
            client: TestClient,
            category_with_three_questions: CategoryPublic
    ) -> None:
        res = await client.get(
            app.url_path_for("question:get-list-for-category", category_id=category_with_three_questions.id)
        )
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0

        for fetched_question, created_question in zip(res.json(), category_with_three_questions.questions):
            assert fetched_question == created_question

    async def test_get_question_by_id_for_category(
            self,
            app: FastAPI,
            client: TestClient,
            category_with_one_question: CategoryPublic
    ) -> None:
        first_created_question = category_with_one_question.questions[0]
        res = await client.get(app.url_path_for(
            "question:get-by-id",
            category_id=category_with_one_question.id,
            question_id=first_created_question["id"]
        ))
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == first_created_question

    async def test_get_question_by_wrong_id_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            empty_category: CategoryPublic,
            random_object_id_str: str
    ) -> None:
        res = await client.get(app.url_path_for(
            "question:get-by-id",
            category_id=empty_category.id,
            question_id=random_object_id_str
        ))
        assert res.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_question_from_wrong_category_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            category_list: List[CategoryPublic]
    ) -> None:
        res = await client.get(app.url_path_for(
            "question:get-by-id",
            category_id=category_list[0].id,
            question_id=category_list[1].questions[0]["id"]
        ))
        assert res.status_code == status.HTTP_404_NOT_FOUND


class TestCreateQuestion:
    """
    Check question creation with and without valid input
    """

    async def test_valid_input_creates_question_for_category(
            self,
            app: FastAPI,
            client: TestClient,
            empty_category: CategoryPublic,
            question_factory: Callable
    ) -> None:
        new_question_dict = question_factory(0).model_dump()
        res = await client.post(
            app.url_path_for("question:create", category_id=empty_category.id),
            json=new_question_dict
        )
        assert res.status_code == status.HTTP_201_CREATED

        fetched_question = res.json()
        assert fetched_question["category_id"] == str(empty_category.id)
        for key, value in new_question_dict.items():
            assert fetched_question[key] == value

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
                (None, 422),
                ({}, 422),
                ({"question": "Who?", "answer": "Me"}, 422),
                ({"question": "Who?", "value": 10}, 422),
                ({"answer": "Me", "value": 10}, 422),
                ({"question": "Who?", "answer": None, "value": 10}, 422),
                ({"question": "", "answer": "Me", "value": 10}, 422),
                ({"question": "Who?", "answer": "", "value": 10}, 422),
                ({"question": "Who?", "answer": "Me", "value": None}, 422),
                ({"question": "Who?", "answer": "Me", "value": 0}, 422),
                ({"question": "Who?", "answer": "Me", "value": -10}, 422),
                ({"question": "Who?", "answer": "Me", "value": 1.5}, 422),
        ),
    )
    async def test_invalid_input_for_create_question_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            empty_category: CategoryPublic,
            invalid_payload,
            status_code
    ) -> None:
        res = await client.post(
            app.url_path_for("question:create", category_id=empty_category.id),
            json=invalid_payload
        )
        assert res.status_code == status_code


class TestUpdateQuestion:
    """
    Check question update
    """

    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
                (["question"], ["Updated question"]),
                (["question", "answer"], ["Updated question", "Updated answer"]),
                (["answer", "value"], ["Updated answer", 1]),
        ),
    )
    async def test_valid_input_updates_question_for_category(
            self,
            app: FastAPI,
            client: TestClient,
            category_with_one_question: CategoryPublic,
            attrs_to_change: List[str],
            values: List[str | int]
    ) -> None:
        original_question_dict = category_with_one_question.questions[0]
        question_update = {attrs_to_change[i]: values[i] for i in range(len(attrs_to_change))}
        res = await client.put(
            app.url_path_for(
                "question:update-by-id",
                category_id=category_with_one_question.id,
                question_id=original_question_dict["id"]
            ),
            json=question_update
        )
        assert res.status_code == status.HTTP_200_OK

        fetched_question = res.json()
        # make sure that any attribute we updated has changed to the correct value
        for i in range(len(attrs_to_change)):
            assert fetched_question.get(attrs_to_change[i]) != original_question_dict.get(attrs_to_change[i])
            assert fetched_question.get(attrs_to_change[i]) == values[i]
        # make sure that no other attributes' values have changed
        for key, value in fetched_question.items():
            if key not in attrs_to_change:
                assert original_question_dict.get(key) == value

    @pytest.mark.parametrize(
        "payload, status_code",
        (
                (None, 422),
                ({}, 304),
                ({"non-existent": "field"}, 304),
                ({"question": None}, 304),
                ({"question": ""}, 422),
                ({"answer": None}, 304),
                ({"answer": ""}, 422),
                ({"value": None}, 304),
                ({"value": 0}, 422),
                ({"value": -1}, 422),
                ({"value": 1.5}, 422),
        ),
    )
    async def test_invalid_input_updates_question_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            category_with_one_question: CategoryPublic,
            payload: Dict[str, str | int],
            status_code: int
    ) -> None:
        original_question_dict = category_with_one_question.questions[0]
        res = await client.put(
            app.url_path_for(
                "question:update-by-id",
                category_id=category_with_one_question.id,
                question_id=original_question_dict["id"]
            ),
            json=payload
        )
        assert res.status_code == status_code

    async def test_update_question_for_wrong_category_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            category_list: List[CategoryPublic]
    ) -> None:
        res = await client.put(
            app.url_path_for(
                "question:update-by-id",
                category_id=category_list[0].id,
                question_id=category_list[1].questions[0]["id"]
            ),
            json={"answer": "Wrong category id"}
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteQuestion:
    """
    Check question deletion
    """
    async def test_delete_question_from_category(
            self,
            app: FastAPI,
            client: TestClient,
            category_with_one_question: CategoryPublic
    ) -> None:
        res = await client.delete(app.url_path_for(
            "question:delete-by-id",
            category_id=category_with_one_question.id,
            question_id=category_with_one_question.questions[0]["id"]
        ))
        assert res.status_code == status.HTTP_204_NO_CONTENT

        confirm_res = await client.get(app.url_path_for(
            "question:get-list-for-category",
            category_id=category_with_one_question.id
        ))
        assert confirm_res.status_code == status.HTTP_200_OK
        assert len(confirm_res.json()) == 0

    async def test_delete_question_with_wrong_id_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            empty_category: CategoryPublic,
            random_object_id_str: str
    ) -> None:
        res = await client.delete(app.url_path_for(
            "question:delete-by-id",
            category_id=empty_category.id,
            question_id=random_object_id_str
        ))
        assert res.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_question_from_wrong_category_raises_error(
            self,
            app: FastAPI,
            client: TestClient,
            category_list: List[CategoryPublic]
    ) -> None:
        res = await client.delete(app.url_path_for(
            "question:delete-by-id",
            category_id=category_list[0].id,
            question_id=category_list[1].questions[0]["id"]
        ))
        assert res.status_code == status.HTTP_404_NOT_FOUND
    