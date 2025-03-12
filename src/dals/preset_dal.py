from sqlalchemy import select

from jlib.dals import BasePresetDAL, RelationalDAL
from jlib.schemas.preset import PresetCreateSchema
from models.preset import PresetModel


class PresetDAL(BasePresetDAL, RelationalDAL):
    async def select(self, user_id: int, offset: int, limit: int) -> list[PresetModel]:
        stmt = (
            select(PresetModel)
            .where(PresetModel.owner_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        return await self.scalars(stmt)

    async def create(self, preset: PresetCreateSchema) -> PresetModel:
        preset_in_db = PresetModel(**preset.model_dump())
        async with self.session() as session:
            session.add(preset_in_db)
            await session.flush()
            await session.refresh(preset_in_db)
        return preset_in_db
