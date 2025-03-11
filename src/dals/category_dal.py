from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from jlib.dals import BaseCategoryDAL, RelationalDAL
from jlib.schemas.category import CategoryCreateSchema, CategoryPartialUpdateSchema
from models.category import CategoryModel


class CategoryDAL(BaseCategoryDAL, RelationalDAL):
    async def select_by_id(self, category_id: int) -> CategoryModel | None:
        stmt = (
            select(CategoryModel)
            .options(selectinload(CategoryModel.prompts))
            .where(CategoryModel.id == category_id)
        )
        return await self.scalar(stmt)

    async def select_by_name(self, category_name: str) -> CategoryModel | None:
        stmt = (
            select(CategoryModel)
            .options(selectinload(CategoryModel.prompts))
            .where(CategoryModel.name == category_name)
        )
        return await self.scalar(stmt)

    async def select(self, offset: int, limit: int) -> list[CategoryModel]:
        stmt = select(CategoryModel).offset(offset).limit(limit)
        return await self.scalars(stmt)

    async def create(self, category: CategoryCreateSchema) -> CategoryModel:
        category_in_db = CategoryModel(**category.model_dump())
        async with self.session() as session:
            session.add(category_in_db)
            await session.flush()
            await session.refresh(category_in_db)
        return category_in_db

    async def update(
        self,
        category_id: int,
        category: CategoryPartialUpdateSchema,
    ) -> None:
        stmt = (
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(**category.model_dump())
        )
        await self.execute(stmt)

    async def delete(self, category_id: int) -> None:
        stmt = delete(CategoryModel).where(CategoryModel.id == category_id)
        await self.execute(stmt)
