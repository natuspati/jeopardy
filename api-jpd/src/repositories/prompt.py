from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.orm import selectinload

from models.prompt import PromptModel
from repositories.mixins import RelationalRepoMixin
from schemas.prompt.base import BasePromptSchema, PromptCreateSchema, PromptUpdateSchema
from schemas.prompt.nested import PromptSchema
from utils.validation import validate_model


class PromptRepo(RelationalRepoMixin):
    async def select(self, prompt_id: int, category_id: int | None = None) -> PromptSchema | None:
        stmt = select(PromptModel).options(selectinload(PromptModel.category))

        filters = [PromptModel.id == prompt_id]
        if category_id is not None:
            filters.append(PromptModel.category_id == category_id)

        stmt = stmt.where(and_(*filters))

        prompt = await self.scalar(stmt)
        return validate_model(prompt, PromptSchema)

    async def insert(self, prompt: PromptCreateSchema) -> BasePromptSchema:
        stmt = insert(PromptModel).values(prompt.model_dump()).returning(PromptModel)
        created_prompt = await self.scalar(stmt)
        return validate_model(created_prompt, BasePromptSchema)

    async def update(self, prompt_id: int, prompt: PromptUpdateSchema) -> BasePromptSchema:
        stmt = (
            update(PromptModel)
            .values(prompt.model_dump(exclude_unset=True, exclude_none=True))
            .where(PromptModel.id == prompt_id)
            .returning(PromptModel)
        )
        updated_prompt = await self.scalar(stmt)
        return validate_model(updated_prompt, BasePromptSchema)

    async def delete(self, prompt_id: int) -> None:
        stmt = delete(PromptModel).where(PromptModel.id == prompt_id)
        await self.execute(stmt)
