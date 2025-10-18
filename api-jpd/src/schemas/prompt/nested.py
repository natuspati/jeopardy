from schemas.category.base import BaseCategorySchema
from schemas.prompt.base import BasePromptSchema


class PromptSchema(BasePromptSchema):
    category: BaseCategorySchema
