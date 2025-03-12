from abc import ABC, abstractmethod

from jlib.schemas.preset import PaginatedBasicPresetSchema


class BasePresetService(ABC):
    @abstractmethod
    async def get_presets(self, **kwargs) -> PaginatedBasicPresetSchema:
        pass
