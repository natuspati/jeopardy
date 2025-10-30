from typing import Annotated

from fastapi import Depends

from errors.auth import ForbiddenError
from errors.request import BadRequestError, NotFoundError
from errors.storage import DBError
from repositories import PromptRepo
from schemas.category.nested import CategorySchema
from schemas.prompt.base import (
    BasePromptSchema,
    PromptCreatePublicSchema,
    PromptCreateSchema,
    PromptUpdateSchema,
)
from schemas.prompt.nested import PromptSchema
from services.category import CategoryService


class PromptService:
    def __init__(
        self,
        prompt_repo: Annotated[PromptRepo, Depends()],
        category_service: Annotated[CategoryService, Depends()],
    ):
        self._prompt_repo = prompt_repo
        self._category_service = category_service

    async def get_prompt(self, prompt_id: int, category_id: int | None = None) -> PromptSchema:
        prompt = await self._prompt_repo.select(prompt_id=prompt_id, category_id=category_id)
        if not prompt:
            raise NotFoundError(f"Prompt {prompt_id} not found")
        return prompt

    async def create_prompt(
        self,
        prompt: PromptCreatePublicSchema,
        category_id: int,
        user_id: int,
    ) -> BasePromptSchema:
        category = await self._check_category_permissions(category_id=category_id, user_id=user_id)
        if category.is_full:
            raise BadRequestError("Category is full")
        if prompt.order in {p.order for p in category.prompts}:
            raise BadRequestError("Prompt with this order already exists")

        prompt_with_category = PromptCreateSchema(
            category_id=category_id,
            **prompt.model_dump(exclude_unset=True, exclude_none=True),
        )
        try:
            return await self._prompt_repo.insert(prompt_with_category)
        except DBError as error:
            raise BadRequestError("Invalid prompt order in the category") from error

    async def update_prompt(
        self,
        prompt_id: int,
        category_id: int,
        prompt: PromptUpdateSchema,
        user_id: int,
    ) -> BasePromptSchema:
        await self._check_category_permissions(category_id=category_id, user_id=user_id)
        return await self._prompt_repo.update(prompt_id=prompt_id, prompt=prompt)

    async def delete_prompt(self, prompt_id: int, category_id: int, user_id: int) -> None:
        await self._check_category_permissions(category_id=category_id, user_id=user_id)
        return await self._prompt_repo.delete(prompt_id=prompt_id)

    async def _check_category_permissions(self, category_id: int, user_id: int) -> CategorySchema:
        category = await self._category_service.get_category(category_id)
        if category.owner_id != user_id:
            raise ForbiddenError(f"Category {category_id} is not owned by user {user_id}")
        return category
