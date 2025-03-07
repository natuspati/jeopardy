from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.v1 import prompt
from jlib.errors.resource import ResourceNotFoundError
from jlib.schemas.category import (
    BasicCategoryShowSchema,
    CategoryCreateSchema,
    CategoryCreateShowSchema,
    CategoryFullUpdateSchema,
    CategoryShowSchema,
    CategoryUpdateShowSchema,
)
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.user import UserSchema
from jlib.services.question_service import BaseQuestionService
from jlib.utils.response import generate_responses
from services.auth_service import get_current_user
from services.question_service import QuestionService

router = APIRouter(prefix="/category", tags=["question"])
router.include_router(prompt.router)


@router.get("/", response_model=list[BasicCategoryShowSchema])
async def get_categories(
    pagination: Annotated[PaginationSchema, Query()],
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    return await question_service.get_categories(pagination=pagination)


@router.get(
    "/{category_id}",
    response_model=CategoryShowSchema,
    responses=generate_responses(
        (status.HTTP_404_NOT_FOUND, "Category not found"),
    ),
)
async def get_category(
    category_id: int,
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    category = await question_service.get_category_by_id(category_id)
    if not category:
        raise ResourceNotFoundError(f"Category with id {category_id} not found")
    return category


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BasicCategoryShowSchema,
    responses=generate_responses(
        (status.HTTP_409_CONFLICT, "Category with a given name already exists"),
    ),
)
async def create_category(
    category: CategoryCreateShowSchema,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    return await question_service.create_category(
        CategoryCreateSchema(
            owner_id=current_user.id,
            **category.model_dump(),
        )
    )


@router.patch("/{category_id}", response_model=CategoryShowSchema)
async def update_category(
    category_id: int,
    category_update: CategoryUpdateShowSchema,
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    return await question_service.update_category(
        CategoryFullUpdateSchema(
            id=category_id,
            **category_update.model_dump(),
        ),
    )


@router.delete("/{category_id}", response_model=None)
async def delete_category(
    category_id: int,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    question_service: Annotated[BaseQuestionService, Depends(QuestionService)],
):
    return await question_service.delete_category(category_id, current_user.id)
