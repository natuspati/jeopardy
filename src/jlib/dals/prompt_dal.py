from abc import ABC, abstractmethod

from jlib.schemas.category import PromptCategorySchema
from jlib.schemas.prompt import (
    PromptCreateSchema,
    PromptPriorityUpdateSchema,
    PromptUpdateSchema,
)


class BasePromptDAL(ABC):
    @abstractmethod
    async def select_by_id(self, prompt_id: int) -> PromptCategorySchema | None:
        pass

    @abstractmethod
    async def create(self, prompt: PromptCreateSchema):
        pass

    @abstractmethod
    async def update_priorities(
        self,
        priority_updates: list[PromptPriorityUpdateSchema],
    ) -> None:
        pass

    @abstractmethod
    async def update(self, prompt: PromptUpdateSchema) -> None:
        pass

    @abstractmethod
    async def delete(self, prompt_id: int) -> None:
        pass
