from typing import Annotated

from fastapi import Depends

from dals import PresetDAL
from jlib.dals import BasePresetDAL
from jlib.errors.auth import ForbiddenError
from jlib.errors.resource import ResourceNotFoundError
from jlib.schemas.pagination import PaginationSchema
from jlib.schemas.preset import (
    BasicPresetSchema,
    PaginatedBasicPresetSchema,
    PresetCreateSchema,
    PresetSchema,
    PresetUpdateSchema,
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

    async def get_preset(self, preset_id: int, user_id: int) -> PresetSchema:
        preset = await self._preset_dal.select_by_id(preset_id)
        if not preset:
            raise ResourceNotFoundError(f"Preset with id {preset_id} does not exist")
        if preset.owner_id != user_id:
            raise ForbiddenError(f"User does not own the preset {preset_id}")
        return self._validate(preset, PresetSchema)

    async def create_preset(self, preset: PresetCreateSchema) -> BasicPresetSchema:
        created_preset = await self._preset_dal.create(preset)
        return self._validate(created_preset, BasicPresetSchema)

    async def update_preset(self, preset_update: PresetUpdateSchema) -> PresetSchema:
        preset = await self._preset_dal.select_by_id(preset_update.id)
        if not preset:
            raise ResourceNotFoundError(
                f"Preset with id {preset_update.id} does not exist"
            )
        if preset.owner_id != preset_update.owner_id:
            raise ForbiddenError(f"User does not own the preset {preset_update.id}")
        updated_preset = await self._preset_dal.update(preset_update)
        return self._validate(updated_preset, PresetSchema)

    async def delete_preset(self, preset_id: int, user_id: int) -> None:
        preset = await self._preset_dal.select_by_id(preset_id)
        if not preset:
            return None
        if preset.owner_id != user_id:
            raise ForbiddenError(f"User does not own the preset {preset_id}")
        await self._preset_dal.delete(preset_id)
