from typing import List

from fastapi import Path, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from app.api.dependencies.category import get_category_by_id_from_path
from app.api.dependencies.database import get_repository

from app.db.repositories.questions import QuestionRepository

from app.models.category import CategoryInDB
from app.models.question import QuestionPublic


async def get_question_by_id_from_path(
        question_id: str = Path(...),
        category: CategoryInDB = Depends(get_category_by_id_from_path),
        question_repo: QuestionRepository = Depends(get_repository(QuestionRepository)),
) -> QuestionPublic:
    question = await question_repo.get_question_by_id(
        category_id=category.id,
        question_id=question_id
    )
    
    if not question:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"No question found with id: {question_id} in the category",
        )
    
    return question


async def list_questions_for_category_by_id_from_path(
        category: CategoryInDB = Depends(get_category_by_id_from_path),
        question_repo: QuestionRepository = Depends(get_repository(QuestionRepository)),
) -> List[QuestionPublic]:
    return await question_repo.list_questions_for_category(category_id=category.id)
