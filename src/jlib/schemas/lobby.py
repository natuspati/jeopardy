import uuid
from typing import Annotated

from pydantic import AfterValidator, Field

from jlib.enums import LobbyMemberTypeEnum, LobbyStateEnum
from jlib.schemas.base import BaseSchema
from jlib.schemas.category import CategoryInGameSchema
from jlib.schemas.player import PlayerSchema


def _check_players(players: list[PlayerSchema]) -> list[PlayerSchema]:
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


class LobbyCreateSchema(BaseSchema):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    state: LobbyStateEnum = LobbyStateEnum.CREATED
    players: Annotated[list[PlayerSchema], AfterValidator(_check_players)]
    categories: Annotated[list[CategoryInGameSchema], AfterValidator(_check_categories)]


class LobbyUpdateSchema(BaseSchema):
    id: uuid.UUID
    state: LobbyStateEnum
    players: list[PlayerSchema]
    categories: list[CategoryInGameSchema]
