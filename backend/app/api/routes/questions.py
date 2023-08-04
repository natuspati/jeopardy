from typing import List

from fastapi import APIRouter, Body, Depends, Security

from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.category import get_category_by_id_from_path
from app.api.dependencies.question import list_questions_for_category_by_id_from_path, get_question_by_id_from_path

from app.db.repositories.questions import QuestionRepository
from app.models.category import CategoryInDB
from app.models.question import QuestionPublic, QuestionCreate, QuestionUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=List[QuestionPublic],
    response_description="List all questions for a category",
    name="question:get-list-for-category"
)
async def list_questions_for_category(
        questions: List[QuestionPublic] = Depends(list_questions_for_category_by_id_from_path),
) -> List[QuestionPublic]:
    return questions


@router.get(
    "/{question_id}/",
    response_model=QuestionPublic,
    response_description="Get question by id",
    name="question:get-by-id"
)
async def get_question_by_id(
        question: QuestionPublic = Depends(get_question_by_id_from_path),
) -> QuestionPublic:
    return question


@router.post(
    "/",
    response_model=QuestionPublic,
    status_code=HTTP_201_CREATED,
    response_description="Create a new question",
    name="question:create",
    dependencies=[Security(get_current_active_user, scopes=["resources"])]
)
async def create_new_question(
        question: QuestionCreate = Body(),
        category: CategoryInDB = Depends(get_category_by_id_from_path),
        question_repo: QuestionRepository = Depends(get_repository(QuestionRepository))
) -> QuestionPublic:
    return await question_repo.create_question(question=question, category=category)


@router.put(
    "/{question_id}/",
    response_model=QuestionPublic,
    response_description="Update question by id",
    name="question:update-by-id",
    dependencies=[Security(get_current_active_user, scopes=["resources"])]
)
async def update_question_by_id(
        question_update: QuestionUpdate = Body(),
        question: QuestionPublic = Depends(get_question_by_id_from_path),
        question_repo: QuestionRepository = Depends(get_repository(QuestionRepository)),
) -> QuestionPublic:
    return await question_repo.update_question_by_id(question=question, question_update=question_update)


@router.delete(
    "/{question_id}",
    status_code=HTTP_204_NO_CONTENT,
    response_description="Delete question by id",
    name="question:delete-by-id",
    dependencies=[Security(get_current_active_user, scopes=["resources"])]
)
async def delete_question_by_id(
        question: QuestionPublic = Depends(get_question_by_id_from_path),
        question_repo: QuestionRepository = Depends(get_repository(QuestionRepository)),
) -> None:
    return await question_repo.delete_question_by_id(question=question)
