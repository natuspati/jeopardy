import re
from typing import Annotated

from fastapi.params import Depends

from errors.auth import ForbiddenError
from errors.request import BadRequestError, NotFoundError
from repositories import CategoryRepo
from schemas.category.base import (
    BaseCategorySchema,
    CategoryCreatePublicSchema,
    CategoryCreateSchema,
)
from schemas.category.nested import CategorySchema, CategoryUpdateSchema
from schemas.prompt.base import PromptOrderUpdateSchema


class CategoryService:
    def __init__(self, category_repo: Annotated[CategoryRepo, Depends()]):
        self._category_repo = category_repo

    async def get_category(self, category_id: int) -> CategorySchema:
        category = await self._category_repo.select(category_id)
        if not category:
            raise NotFoundError(f"Category {category_id} not found")
        return category

    async def search_categories(
        self,
        category_ids: list[int] | None = None,
        name: str | None = None,
    ) -> list[CategorySchema]:
        if name is not None:
            name = self._clean_search_term(name)
        return await self._category_repo.filter(category_ids=category_ids, name=name)

    async def create_category(
        self,
        category: CategoryCreatePublicSchema,
        user_id: int,
    ) -> BaseCategorySchema:
        category_with_owner = CategoryCreateSchema(owner_id=user_id, **category.model_dump())
        return await self._category_repo.insert(category_with_owner)

    async def update_category(
        self,
        category_id: int,
        category: CategoryUpdateSchema,
        user_id: int,
    ) -> CategorySchema:
        existing_cat = await self._check_permissions(user_id=user_id, category_id=category_id)

        if category.prompts is not None:
            self._check_prompt_order_update(existing_cat, category.prompts)

        await self._category_repo.update(category_id, category)
        return await self.get_category(category_id)

    async def delete_category(self, category_id: int, user_id: int) -> None:
        await self._check_permissions(user_id=user_id, category_id=category_id)
        await self._category_repo.delete(category_id)

    async def _check_permissions(self, user_id: int, category_id: int) -> CategorySchema:
        category = await self.get_category(category_id)
        if category.owner_id != user_id:
            raise ForbiddenError(f"Category {category_id} is not owned by user {user_id}")
        return category

    @classmethod
    def _check_prompt_order_update(
        cls,
        category: CategorySchema,
        new_prompts: list[PromptOrderUpdateSchema],
    ) -> None:
        existing_prompt_ids = {p.id for p in category.prompts}
        new_prompt_ids = {p.id for p in new_prompts}

        if existing_prompt_ids != new_prompt_ids:
            missing = existing_prompt_ids - new_prompt_ids
            extra = new_prompt_ids - existing_prompt_ids

            if missing:
                raise BadRequestError(f"Missing prompts in update: {sorted(missing)}")
            if extra:
                raise BadRequestError(f"Unknown prompts in update: {sorted(extra)}")

        if len(existing_prompt_ids) != len(new_prompt_ids):
            raise BadRequestError(
                "Updating prompt order must include all prompts from the category",
            )

    @classmethod
    def _clean_search_term(cls, term: str) -> str:
        clean = term.strip()

        if not clean:
            raise BadRequestError("Search query parameter cannot be empty.")

        if any(c in clean for c in ("%", "_")):
            raise BadRequestError("Search query parameter has invalid characters.")

        if not re.match(r"^[\w\s\-'.!?]+$", clean):
            raise BadRequestError("Search query parameter has invalid characters.")

        return clean
