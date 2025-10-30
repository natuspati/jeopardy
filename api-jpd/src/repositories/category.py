from sqlalchemy import and_, case, delete, insert, select, update
from sqlalchemy.orm import selectinload

from configs import settings
from models.category import CategoryModel
from models.prompt import PromptModel
from repositories.mixins import RelationalRepoMixin
from schemas.category.base import BaseCategorySchema, CategoryCreateSchema
from schemas.category.nested import CategorySchema, CategoryUpdateSchema
from utils.validation import validate_model


class CategoryRepo(RelationalRepoMixin):
    async def select(self, category_id: int) -> CategorySchema | None:
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.id == category_id)
            .options(
                selectinload(CategoryModel.owner),
                selectinload(CategoryModel.prompts),
                selectinload(CategoryModel.lobbies),
                selectinload(CategoryModel.lobby_categories),
            )
        )
        category = await self.scalar(stmt)
        return validate_model(category, CategorySchema)

    async def filter(
        self,
        category_ids: list[int] | None = None,
        name: str | None = None,
    ) -> list[CategorySchema]:
        filters = []
        if category_ids:
            filters.append(CategoryModel.id.in_(category_ids))
        if name is not None:
            filters.append(CategoryModel.name.ilike(f"%{name}%"))

        stmt = (
            select(CategoryModel)
            .options(
                selectinload(CategoryModel.owner),
                selectinload(CategoryModel.prompts),
                selectinload(CategoryModel.lobbies),
                selectinload(CategoryModel.lobby_categories),
            )
            .limit(settings.page_size)
        )
        if filters:
            stmt = stmt.where(and_(*filters))
        categories = await self.scalars(stmt)
        return validate_model(categories, CategorySchema)

    async def insert(self, category: CategoryCreateSchema) -> BaseCategorySchema:
        stmt = insert(CategoryModel).values(category.model_dump()).returning(CategoryModel)
        created_category = await self.scalar(stmt)
        return validate_model(created_category, BaseCategorySchema)

    async def update(self, category_id: int, category: CategoryUpdateSchema) -> None:
        if category.name is not None:
            stmt = (
                update(CategoryModel)
                .where(CategoryModel.id == category_id)
                .values(name=category.name)
            )
            await self.execute(stmt)

        if category.prompts is not None:
            mapping = {p.id: p.order for p in category.prompts}

            stmt = (
                update(PromptModel)
                .where(PromptModel.id.in_(mapping.keys()))
                .values(order=case(mapping, value=PromptModel.id))
            )
            await self.execute(stmt)

    async def delete(self, category_id: int) -> None:
        stmt = delete(CategoryModel).where(CategoryModel.id == category_id)
        await self.execute(stmt)
