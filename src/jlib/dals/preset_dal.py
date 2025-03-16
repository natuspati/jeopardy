from abc import ABC, abstractmethod

from jlib.schemas.preset import (
    BasicPresetSchema,
    PresetCreateSchema,
    PresetSchema,
    PresetUpdateSchema,
)


class BasePresetDAL(ABC):
    @abstractmethod
    async def select(self, **filters: int | str) -> list[BasicPresetSchema]:
        pass

    @abstractmethod
    async def select_by_id(self, preset_id: int) -> PresetSchema | None:
        pass

    @abstractmethod
    async def create(self, preset: PresetCreateSchema) -> BasicPresetSchema:
        pass

    @abstractmethod
    async def update(self, preset: PresetUpdateSchema) -> PresetSchema:
        pass

    @abstractmethod
    async def delete(self, preset_id: int) -> None:
        pass
