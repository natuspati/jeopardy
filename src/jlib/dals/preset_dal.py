from abc import ABC, abstractmethod

from jlib.schemas.preset import PresetCreateSchema, PresetUpdateSchema


class BasePresetDAL(ABC):
    @abstractmethod
    async def select(self, **kwargs):
        pass

    @abstractmethod
    async def select_by_id(self, preset_id: int):
        pass

    @abstractmethod
    async def create(self, preset: PresetCreateSchema):
        pass

    @abstractmethod
    async def update(self, preset: PresetUpdateSchema):
        pass

    @abstractmethod
    async def delete(self, preset_id: int) -> None:
        pass
