from abc import ABC, abstractmethod

from jlib.schemas.preset import PresetCreateSchema


class BasePresetDAL(ABC):
    @abstractmethod
    async def select(self, **kwargs):
        pass

    @abstractmethod
    async def create(self, preset: PresetCreateSchema):
        pass
