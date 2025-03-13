from abc import ABC, abstractmethod

from jlib.schemas.preset import (
    BasicPresetSchema,
    PaginatedBasicPresetSchema,
    PresetCreateSchema,
    PresetSchema,
    PresetUpdateSchema,
)


class BasePresetService(ABC):
    @abstractmethod
    async def get_presets(self, **kwargs) -> PaginatedBasicPresetSchema:
        pass

    @abstractmethod
    async def get_preset(self, preset_id: int, user_id: int) -> PresetSchema:
        pass

    @abstractmethod
    async def create_preset(self, preset: PresetCreateSchema) -> BasicPresetSchema:
        pass

    @abstractmethod
    async def update_preset(self, preset_update: PresetUpdateSchema) -> PresetSchema:
        pass

    @abstractmethod
    async def delete_preset(self, preset_id: int, user_id: int) -> None:
        pass
