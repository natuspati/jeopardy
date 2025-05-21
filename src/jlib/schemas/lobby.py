import uuid
from typing import Annotated

from pydantic import AfterValidator, Field

from jlib.enums import LobbyMemberTypeEnum, LobbyStateEnum
from jlib.schemas.base import BaseSchema
from jlib.schemas.category import CategoryInGameSchema
from jlib.schemas.pagination import PaginatedResponseSchema
from jlib.schemas.player import PlayerSchema
from jlib.schemas.prompt import PromptInGameSchema
from jlib.schemas.user import UserSchema


def _check_update_players(players: list[PlayerSchema] | None) -> list[PlayerSchema] | None:
    if players is None:
        return None

    lead_players = [p for p in players if p.type == LobbyMemberTypeEnum.LEAD]
    if not lead_players:
        raise ValueError("At least one player must be lead.")
    elif len(lead_players) > 1:
        raise ValueError("Only one player can be lead.")

    selected_players = [p for p in players if p.selected]
    if len(selected_players) > 1:
        raise ValueError("No more than one player can be selected.")

    return players


def _check_players_for_lead(players: list[PlayerSchema]) -> list[PlayerSchema]:
    """
    Check whether there is at least one lead player.
    """
    if not players:
        raise ValueError("At least one player must be registered.")

    lead_players = [p for p in players if p.type == LobbyMemberTypeEnum.LEAD]

    if not lead_players:
        raise ValueError("At least one player must be lead.")
    elif len(lead_players) > 1:
        raise ValueError("Only one player can be lead.")

    return players


def _check_categories(
    categories: list[CategoryInGameSchema],
) -> list[CategoryInGameSchema]:
    """
    Check whether the categories are unique and same number of prompts per category.
    """
    category_ids = {cat.id for cat in categories}
    if len(category_ids) != len(categories):
        raise ValueError("Categories must be unique.")

    num_prompts = len(categories[0].prompts)
    if any(len(cat.prompts) != num_prompts for cat in categories[1:]):
        raise ValueError("All categories must have the same number of prompts.")
    return categories


class LobbySchema(BaseSchema):
    id: uuid.UUID
    state: LobbyStateEnum
    players: list[PlayerSchema]
    categories: list[CategoryInGameSchema]

    @property
    def lead(self) -> PlayerSchema:
        return next(player for player in self.players if player.type == LobbyMemberTypeEnum.LEAD)

    @property
    def selected(self) -> PlayerSchema | None:
        return next((player for player in self.players if player.selected), None)

    def __contains__(self, user_id: int) -> bool:
        return any(player.user_id == user_id for player in self.players)

    def __getitem__(self, user_id: int) -> PlayerSchema | None:
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None

    def pop_player(self, user_id: int) -> PlayerSchema | None:
        for i, player in enumerate(self.players):
            if player.user_id == user_id:
                return self.players.pop(i)
        return None

    def get_prompt(self, prompt_id: int) -> PromptInGameSchema | None:
        for category in self.categories:
            for prompt in category.prompts:
                if prompt.id == prompt_id:
                    return prompt
        return None


class BasicLobbySchema(BaseSchema):
    id: uuid.UUID
    state: LobbyStateEnum
    num_players: int


class LobbyCreateShowSchema(BaseSchema):
    preset_id: int


class LobbyCreateFromPresetSchema(LobbyCreateShowSchema):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    state: LobbyStateEnum = LobbyStateEnum.CREATE
    user: UserSchema
    preset_id: int


class LobbyCreateSchema(BaseSchema):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    state: LobbyStateEnum = LobbyStateEnum.CREATE
    players: Annotated[list[PlayerSchema], AfterValidator(_check_players_for_lead)]
    categories: Annotated[list[CategoryInGameSchema], AfterValidator(_check_categories)]


class LobbyUpdateSchema(BaseSchema):
    id: uuid.UUID
    state: LobbyStateEnum | None = None
    players: Annotated[list[PlayerSchema] | None, AfterValidator(_check_update_players)] = None
    categories: Annotated[list[CategoryInGameSchema] | None, AfterValidator(_check_categories)] = (
        None
    )


class LobbyJoinSchema(BasicLobbySchema):
    join_url: str


class PaginatedBasicLobbySchema(PaginatedResponseSchema[BasicLobbySchema]):
    pass
