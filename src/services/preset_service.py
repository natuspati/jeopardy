from typing import Annotated

from fastapi import Depends

from dals import PresetDAL
from jlib.dals import BasePresetDAL
from jlib.errors.auth import ForbiddenError
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.preset import (
    BasicPresetSchema,
    PaginatedBasicPresetSchema,
    PresetCreateSchema,
)
from jlib.services import (
    BasePresetService,
    PaginationServiceMixin,
    SchemaValidationServiceMixin,
)


class PresetService(
    BasePresetService, SchemaValidationServiceMixin, PaginationServiceMixin
):
    def __init__(
        self,
        preset_dal: Annotated[BasePresetDAL, Depends(PresetDAL)],
    ):
        self._preset_dal = preset_dal

    async def get_presets(
        self,
        user_id: int,
        pagination: PaginationSchema,
    ) -> PaginatedBasicPresetSchema:
        self._check_pagination(pagination)
        presets = await self._preset_dal.select(
            user_id=user_id,
            offset=pagination.offset,
            limit=pagination.limit,
        )
        return PaginatedBasicPresetSchema.paginate(
            items=self._validate(presets, BasicPresetSchema),
            pagination=pagination,
        )

    async def create_preset(self, preset: PresetCreateSchema) -> BasicPresetSchema:
        created_preset = await self._preset_dal.create(preset)
        return self._validate(created_preset, BasicPresetSchema)

    async def delete_preset(self, preset_id: int, user_id: int) -> None:
        preset = await self._preset_dal.select_by_id(preset_id)
        if not preset:
            return None
        if preset.owner_id != user_id:
            raise ForbiddenError(f"User does not own the preset {preset_id}")
        await self._preset_dal.delete(preset_id)
