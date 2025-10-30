from pydantic import BaseModel, Field

from enums.game import GameStateEnum
from schemas.category.nested import CategoryInGameSchema
from schemas.player import LeadSchema, PlayerSchema
from schemas.prompt.base import BasePromptSchema


class GameSchema(BaseModel):
    id: int = Field(description="Lobby ID")
    state: GameStateEnum
    lead: LeadSchema
    players: list[PlayerSchema]
    categories: list[CategoryInGameSchema]
    selected_player: PlayerSchema | None = None
    selected_prompt: BasePromptSchema | None = None
