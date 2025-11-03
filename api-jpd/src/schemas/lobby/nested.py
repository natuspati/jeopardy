from schemas.category.nested import CategoryWithPromptsSchema
from schemas.lobby.base import BaseLobbySchema
from schemas.lobby_category.base import BaseLobbyCategorySchema
from schemas.user.base import BaseUserSchema


class LobbySchema(BaseLobbySchema):
    host: BaseUserSchema
    categories: list[CategoryWithPromptsSchema]
    lobby_categories: list[BaseLobbyCategorySchema]

    @property
    def is_valid(self) -> bool:
        return all(category.is_valid for category in self.categories)
