from typing import Annotated

from fastapi import APIRouter, Depends, status

from auth import authenticate_user
from schemas.prompt.base import BasePromptSchema, PromptCreatePublicSchema, PromptUpdateSchema
from schemas.prompt.nested import PromptSchema
from schemas.user.base import BaseUserSchema
from services import PromptService

router = APIRouter(prefix="/{category_id}/prompt", tags=["prompt"])


@router.get("/{prompt_id}", response_model=PromptSchema)
async def get_prompt(
    category_id: int,
    prompt_id: int,
    prompt_service: Annotated[PromptService, Depends()],
):
    return await prompt_service.get_prompt(prompt_id=prompt_id, category_id=category_id)


@router.post("", response_model=BasePromptSchema, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    category_id: int,
    prompt: PromptCreatePublicSchema,
    prompt_service: Annotated[PromptService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    return await prompt_service.create_prompt(
        prompt=prompt,
        category_id=category_id,
        user_id=user.id,
    )


@router.patch("/{prompt_id}", response_model=BasePromptSchema)
async def update_prompt(
    category_id: int,
    prompt_id: int,
    prompt: PromptUpdateSchema,
    prompt_service: Annotated[PromptService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    return await prompt_service.update_prompt(
        prompt_id=prompt_id,
        category_id=category_id,
        prompt=prompt,
        user_id=user.id,
    )


@router.delete("/{prompt_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: int,
    category_id: int,
    prompt_service: Annotated[PromptService, Depends()],
    user: Annotated[BaseUserSchema, Depends(authenticate_user)],
):
    await prompt_service.delete_prompt(
        prompt_id=prompt_id,
        category_id=category_id,
        user_id=user.id,
    )
