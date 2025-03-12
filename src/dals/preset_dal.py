from sqlalchemy import select

from jlib.dals import BasePresetDAL, RelationalDAL
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
