from typing import Annotated

from fastapi import Depends

from dals.category_dal import CategoryDAL
from dals.prompt_dal import PromptDAL
from jlib.dals.category_dal import BaseCategoryDAL
from jlib.dals.prompt_dal import BasePromptDAL
from jlib.errors.auth import ForbiddenError
from jlib.errors.request import BadRequestError
from jlib.errors.resource import ResourceExistsError, ResourceNotFoundError
from jlib.schemas.category import (
    BasicCategorySchema,
    CategoryCreateSchema,
    CategoryFullUpdateSchema,
    CategoryPartialUpdateSchema,
    CategorySchema,
)
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.prompt import PromptCreateSchema, PromptSchema
from jlib.services.base_service import SchemaValidationServiceMixin
from jlib.services.question_service import BaseQuestionService
from settings import settings


class QuestionService(BaseQuestionService, SchemaValidationServiceMixin):
    def __init__(
        self,
        category_dal: Annotated[BaseCategoryDAL, Depends(CategoryDAL)],
        prompt_dal: Annotated[BasePromptDAL, Depends(PromptDAL)],
    ):
        self._category_dal = category_dal
        self._prompt_dal = prompt_dal

    async def get_category_by_id(self, category_id: int) -> CategorySchema | None:
        category = await self._category_dal.select_by_id(category_id)
        if category:
            return self._validate(category, CategorySchema)

    async def get_category_by_name(self, category_name: str) -> CategorySchema | None:
        category = await self._category_dal.select_by_name(category_name)
        if category:
            return self._validate(category, CategorySchema)

    async def get_categories(
        self,
        pagination: PaginationSchema,
    ) -> list[BasicCategorySchema]:
        self._check_pagination(pagination)
        categories = await self._category_dal.select(
            offset=pagination.offset, limit=pagination.limit
        )
        return self._validate(categories, BasicCategorySchema)

    async def create_category(
        self,
        category_create: CategoryCreateSchema,
    ) -> BasicCategorySchema:
        existing_category = await self.get_category_by_name(category_create.name)
        if existing_category:
            raise ResourceExistsError(
                f"Category with name {existing_category.name} already exists"
            )
        created_category = await self._category_dal.create(category_create)
        return self._validate(created_category, BasicCategorySchema)

    async def update_category(
        self, category_update: CategoryFullUpdateSchema
    ) -> CategorySchema:
        category = await self.get_category_by_id(category_update.id)
        if not category:
            raise ResourceNotFoundError(
                f"Category with id {category_update.id} does not exist"
            )
        if category_update.prompts and len(category_update.prompts) != len(
            category.prompts
        ):
            raise BadRequestError("Provided number of prompts does not match")
        if category_update.name:
            await self._category_dal.update(
                category_id=category_update.id,
                category=CategoryPartialUpdateSchema(name=category_update.name),
            )
        if category_update.prompts:
            pass
        return category

    async def delete_category(self, category_id: int, user_id: int) -> None:
        existing_category = await self.get_category_by_id(category_id)
        if existing_category:
            if user_id != existing_category.owner_id:
                raise ForbiddenError(f"User does not own the category {category_id}")
            await self._category_dal.delete(category_id)

    async def create_prompt(self, prompt_create: PromptCreateSchema) -> PromptSchema:
        category = await self.get_category_by_id(prompt_create.category_id)
        if not category:
            raise ResourceNotFoundError(
                f"Category with id {prompt_create.category_id} does not exist"
            )

        existing_priorities = {prompt.default_priority for prompt in category.prompts}
        if prompt_create.default_priority in existing_priorities:
            raise ResourceExistsError(
                f"Prompt with priority {prompt_create.default_priority} already exists"
            )
        created_prompt = await self._prompt_dal.create(prompt_create)
        return self._validate(created_prompt, PromptSchema)

    @classmethod
    def _check_pagination(cls, pagination: PaginationSchema) -> None:
        if pagination.limit is None or pagination.limit > settings.max_query_limit:
            pagination.limit = settings.max_query_limit
