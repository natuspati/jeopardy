from abc import ABC, abstractmethod

from jlib.schemas.preset import (
    BasicPresetSchema,
    PaginatedBasicPresetSchema,
    PresetCreateSchema,
)


class BasePresetService(ABC):
    @abstractmethod
    async def get_presets(self, **kwargs) -> PaginatedBasicPresetSchema:
        pass

    @abstractmethod
    async def create_preset(self, preset: PresetCreateSchema) -> BasicPresetSchema:
        pass
