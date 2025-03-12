from abc import ABC, abstractmethod


class BasePresetDAL(ABC):
    @abstractmethod
    @abstractmethod
    async def select(self, **kwargs):
        pass
