from schemas.category.base import BaseCategorySchema
from schemas.lobby.base import BaseLobbySchema
from schemas.lobby_category.base import BaseLobbyCategorySchema


class LobbyCategorySchema(BaseLobbyCategorySchema):
    lobby: BaseLobbySchema
    category: BaseCategorySchema
