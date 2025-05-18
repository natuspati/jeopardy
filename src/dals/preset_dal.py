from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from jlib.dals import BasePresetDAL, RelationalDAL
from jlib.schemas.preset import (
    BasicPresetSchema,
    PresetCreateSchema,
    PresetSchema,
    PresetUpdateSchema,
)
from jlib.utils.validation import validate_model
from models.category import CategoryModel
from models.preset import PresetModel
from models.preset_category import PresetCategoryModel


class PresetDAL(BasePresetDAL, RelationalDAL):
    async def select(
        self,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[BasicPresetSchema]:
        stmt = (
            select(PresetModel).where(PresetModel.owner_id == user_id).offset(offset).limit(limit)
        )
        presets = await self.scalars(stmt)
        return validate_model(presets, BasicPresetSchema)

    async def select_by_id(self, preset_id: int) -> PresetSchema | None:
        stmt = (
            select(PresetModel)
            .options(
                selectinload(PresetModel.categories).selectinload(CategoryModel.prompts),
            )
            .where(PresetModel.id == preset_id)
        )
        preset = await self.scalar(stmt)
        return validate_model(preset, PresetSchema)

    async def create(self, preset: PresetCreateSchema) -> BasicPresetSchema:
        preset_in_db = PresetModel(**preset.model_dump())
        async with self.session() as session:
            session.add(preset_in_db)
            await session.flush()
            await session.refresh(preset_in_db)
        return validate_model(preset_in_db, BasicPresetSchema)

    async def update(self, preset: PresetUpdateSchema) -> PresetSchema:
        async with self.session() as session:
            if preset.name:
                await self._update_name(session, preset)
            if preset.categories:
                await self._update_categories(session, preset)
        return await self.select_by_id(preset.id)

    async def delete(self, preset_id: int) -> None:
        stmt = delete(PresetModel).where(PresetModel.id == preset_id)
        await self.execute(stmt)

    @classmethod
    async def _update_name(
        cls,
        session: AsyncSession,
        preset: PresetUpdateSchema,
    ) -> None:
        stmt = update(PresetModel).where(PresetModel.id == preset.id).values(name=preset.name)
        await session.execute(stmt)

    @classmethod
    async def _update_categories(
        cls,
        session: AsyncSession,
        preset: PresetUpdateSchema,
    ) -> None:
        existing_stmt = select(PresetCategoryModel.category_id).where(
            PresetCategoryModel.preset_id == preset.id,
        )
        preset_category_ids = set(await session.scalars(existing_stmt))
        to_remove = preset_category_ids - set(preset.categories)
        to_add = set(preset.categories) - preset_category_ids

        if to_remove:
            delete_stmt = delete(PresetCategoryModel).where(
                PresetCategoryModel.preset_id == preset.id,
                PresetCategoryModel.category_id.in_(to_remove),
            )
            await session.execute(delete_stmt)

        if to_add:
            insert_stmt = insert(PresetCategoryModel).values(
                [{"preset_id": preset.id, "category_id": cat_id} for cat_id in to_add],
            )
            await session.execute(insert_stmt)
