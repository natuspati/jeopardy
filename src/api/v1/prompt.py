from typing import Annotated

from fastapi import APIRouter, Depends, status

from auth import get_current_user
from jlib.schemas.prompt import (
    PromptCreateSchema,
    PromptCreateShowSchema,
    PromptShowSchema,
    PromptUpdateSchema,
    PromptUpdateShowSchema,
)
from jlib.schemas.user import UserSchema
from jlib.services import BaseQuestionService
from jlib.utils.response import generate_responses
from services import QuestionService

router = APIRouter(prefix="/{category_id}/prompt")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PromptShowSchema,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
        (status.HTTP_403_FORBIDDEN, "User does not own the category"),
        (status.HTTP_404_NOT_FOUND, "Category not found"),
        (status.HTTP_409_CONFLICT, "Prompt with given priority already exists"),
    ),
)
async def create_prompt(
    category_id: int,
    prompt_crete: PromptCreateShowSchema,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    """
    Create prompt.
    """
    return await question_service.create_prompt(
        user_id=current_user.id,
        prompt_create=PromptCreateSchema(
            category_id=category_id,
            **prompt_crete.model_dump(),
        ),
    )


@router.patch(
    "/{prompt_id}",
    response_model=PromptShowSchema,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
        (status.HTTP_403_FORBIDDEN, "User does not own the category"),
        (status.HTTP_404_NOT_FOUND, "Prompt not found"),
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "Empty data provided"),
    ),
)
async def update_prompt(
    category_id: int,
    prompt_id: int,
    prompt_update: PromptUpdateShowSchema,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    """
    Update prompt.
    """
    return await question_service.update_prompt(
        user_id=current_user.id,
        prompt_update=PromptUpdateSchema(
            id=prompt_id,
            category_id=category_id,
            **prompt_update.model_dump(exclude_none=True),
        ),
    )


@router.delete(
    "/{prompt_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=generate_responses(
        (status.HTTP_401_UNAUTHORIZED, "User not authenticated"),
        (status.HTTP_403_FORBIDDEN, "User does not own the category"),
    ),
)
async def delete_prompt(
    category_id: int,
    prompt_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    """
    Delete prompt.
    """
    return await question_service.delete_prompt(
        user_id=current_user.id,
        category_id=category_id,
        prompt_id=prompt_id,
    )
