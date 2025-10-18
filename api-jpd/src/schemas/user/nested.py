from pydantic import Field

from schemas.category.base import BaseCategorySchema
from schemas.lobby.base import BaseLobbySchema
from schemas.user.base import BaseUserSchema


class UserSchema(BaseUserSchema):
    categories: list[BaseCategorySchema] = Field(default_factory=list)
    lobbies: list[BaseLobbySchema] = Field(default_factory=list)
