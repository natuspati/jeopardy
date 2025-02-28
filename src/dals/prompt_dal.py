from jlib.dals.prompt_dal import BasePromptDAL
from jlib.dals.relational_dal import RelationalDAL
from jlib.schemas.prompt import PromptCreateSchema
from models.prompt import PromptModel


class PromptDAL(BasePromptDAL, RelationalDAL):
    async def create(self, prompt: PromptCreateSchema):
        prompt_in_db = PromptModel(**prompt.model_dump())
        async with self.session() as session:
            session.add(prompt_in_db)
            await session.flush()
            await session.refresh(prompt_in_db)
        return prompt_in_db
