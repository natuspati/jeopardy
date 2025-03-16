from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from jlib.dals import BaseCategoryDAL, RelationalDAL
from jlib.schemas.category import (
    BasicCategorySchema,
    CategoryCreateSchema,
    CategoryPartialUpdateSchema,
    CategorySchema,
)
from jlib.utils.validation import validate_model
from models.category import CategoryModel


class CategoryDAL(BaseCategoryDAL, RelationalDAL):
    async def select_by_id(self, category_id: int) -> CategorySchema | None:
        stmt = (
            select(CategoryModel)
            .options(selectinload(CategoryModel.prompts))
            .where(CategoryModel.id == category_id)
        )
        category = await self.scalar(stmt)
        return validate_model(category, CategorySchema)

    async def select_by_name(self, category_name: str) -> CategorySchema | None:
        stmt = (
            select(CategoryModel)
            .options(selectinload(CategoryModel.prompts))
            .where(CategoryModel.name == category_name)
        )
        category = await self.scalar(stmt)
        return validate_model(category, CategorySchema)

    async def select(self, offset: int, limit: int) -> list[BasicCategorySchema]:
        stmt = select(CategoryModel).offset(offset).limit(limit)
        categories = await self.scalars(stmt)
        return validate_model(categories, BasicCategorySchema)

    async def create(self, category: CategoryCreateSchema) -> BasicCategorySchema:
        category_in_db = CategoryModel(**category.model_dump())
        async with self.session() as session:
            session.add(category_in_db)
            await session.flush()
            await session.refresh(category_in_db)
        return validate_model(category_in_db, BasicCategorySchema)

    async def update(
        self,
        category_id: int,
        category: CategoryPartialUpdateSchema,
    ) -> None:
        stmt = (
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(**category.model_dump(exclude={"id"}))
        )
        await self.execute(stmt)

    async def delete(self, category_id: int) -> None:
        stmt = delete(CategoryModel).where(CategoryModel.id == category_id)
        await self.execute(stmt)
