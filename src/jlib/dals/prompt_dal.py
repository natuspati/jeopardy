from abc import ABC, abstractmethod

from jlib.schemas.prompt import PromptCreateSchema


class BasePromptDAL(ABC):
    @abstractmethod
    async def create(self, prompt: PromptCreateSchema):
        pass
    