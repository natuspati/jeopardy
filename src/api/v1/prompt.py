from typing import Annotated

from fastapi import APIRouter, Depends, status

from jlib.schemas.prompt import (
    PromptCreateSchema,
    PromptCreateShowSchema,
    PromptShowSchema,
)
from jlib.services.question_service import BaseQuestionService
from jlib.utils.response import generate_responses
from services.question_service import QuestionService

router = APIRouter(prefix="/{category_id}/prompt")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PromptShowSchema,
    responses=generate_responses(
        (status.HTTP_404_NOT_FOUND, "Category not found"),
        (status.HTTP_409_CONFLICT, "Prompt with given priority already exists"),
    ),
)
async def create_prompt(
    category_id: int,
    prompt_crete: PromptCreateShowSchema,
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    return await question_service.create_prompt(
        PromptCreateSchema(
            category_id=category_id,
            **prompt_crete.model_dump(),
        )
    )
