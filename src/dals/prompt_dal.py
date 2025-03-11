import asyncio

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from jlib.dals import BasePromptDAL, RelationalDAL
from jlib.schemas.prompt import (
    PromptCreateSchema,
    PromptPriorityUpdateSchema,
    PromptUpdateSchema,
)
from models.prompt import PromptModel


class PromptDAL(BasePromptDAL, RelationalDAL):
    async def select_by_id(self, prompt_id: int) -> PromptModel | None:
        stmt = (
            select(PromptModel)
            .options(selectinload(PromptModel.category))
            .where(PromptModel.id == prompt_id)
        )
        return await self.scalar(stmt)

    async def create(self, prompt: PromptCreateSchema):
        prompt_in_db = PromptModel(**prompt.model_dump(mode="json"))
        async with self.session() as session:
            session.add(prompt_in_db)
            await session.flush()
            await session.refresh(prompt_in_db)
        return prompt_in_db

    async def update_priorities(
        self,
        priority_updates: list[PromptPriorityUpdateSchema],
    ) -> None:
        """
        Update default priorities of prompts.

        Change priority to negative values with an offset, then
        set the priority to the updated value.
        """
        temp_offset = -10
        temp_tasks = [
            self.execute(
                update(PromptModel)
                .where(PromptModel.id == priority.id)
                .values(default_priority=temp_offset + priority.default_priority)
            )
            for priority in priority_updates
        ]
        await asyncio.gather(*temp_tasks)

        final_tasks = [
            self.execute(
                update(PromptModel)
                .where(PromptModel.id == priority.id)
                .values(default_priority=priority.default_priority)
            )
            for priority in priority_updates
        ]
        await asyncio.gather(*final_tasks)

    async def update(self, prompt: PromptUpdateSchema) -> None:
        stmt = (
            update(PromptModel)
            .where(PromptModel.id == prompt.id)
            .values(
                prompt.model_dump(
                    mode="json",
                    exclude_none=True,
                    exclude={"id", "category_id"},
                )
            )
        )
        await self.execute(stmt)
