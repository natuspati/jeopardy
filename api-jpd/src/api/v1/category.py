from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.v1 import prompt
from auth import authenticate_user
from schemas.category.base import BaseCategorySchema, CategoryCreatePublicSchema
from schemas.category.nested import CategorySchema, CategoryUpdateSchema
from schemas.user.base import BaseUserSchema
from services import CategoryService

router = APIRouter(prefix="/category", tags=["prompt"])
router.include_router(prompt.router)


@router.get("", response_model=list[CategorySchema])
async def get_categories(
    category_service: Annotated[CategoryService, Depends()],
    name: Annotated[str | None, Query(min_length=2, max_length=64)] = None,
):
    return await category_service.search_categories(name)


@router.get("/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends()],
):
    return await category_service.get_category(category_id)


@router.post("", response_model=BaseCategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreatePublicSchema,
    category_service: Annotated[CategoryService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    return await category_service.create_category(category=category, user_id=user.id)


@router.patch("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryUpdateSchema,
    category_service: Annotated[CategoryService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    return await category_service.update_category(
        category_id=category_id,
        category=category,
        user_id=user.id,
    )


@router.delete("/{category_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    await category_service.delete_category(category_id=category_id, user_id=user.id)
