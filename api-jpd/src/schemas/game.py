from functools import cached_property

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, computed_field, field_validator

from constants import MAX_NUM_PLAYERS, MIN_NUM_PLAYERS, UnsetSentinel
from enums.game import GameStateEnum
from enums.player import LeadStateEnum, PlayerStateEnum
from enums.prompt import PromptStateEnum
from schemas.base import OneFieldSetMixin, supplied_value_is_not_none
from schemas.category.nested import CategoryInGameSchema
from schemas.player import LeadSchema, PlayerSchema, PlayerUpdateSchema
from schemas.prompt.base import PromptInGameSchema


class GameSchema(BaseModel):
    id: int = Field(description="Lobby ID")
    state: GameStateEnum
    lead: LeadSchema
    players: list[PlayerSchema]
    categories: list[CategoryInGameSchema]

    @computed_field
    @property
    def selected_player(self) -> PlayerSchema | None:
        return next(
            (player for player in self.players if player.state == PlayerStateEnum.SELECTED),
            None,
        )

    @computed_field
    @property
    def selected_prompt(self) -> PromptInGameSchema | None:
        return next(
            (
                prompt
                for category in self.categories
                for prompt in category.prompts
                if prompt.state == PromptStateEnum.SELECTED
            ),
            None,
        )

    @property
    def selected_player_id(self) -> int | None:
        return self.selected_player.id if self.selected_player else None

    @property
    def selected_prompt_id(self) -> int | None:
        return self.selected_prompt.id if self.selected_prompt else None

    @cached_property
    def player_map(self) -> dict[int, PlayerSchema]:
        return {player.id: player for player in self.players}

    @cached_property
    def prompt_map(self) -> dict[int, PromptInGameSchema]:
        return {prompt.id: prompt for category in self.categories for prompt in category.prompts}

    @cached_property
    def active_players_count(self) -> int:
        return sum(
            1
            for player in self.players
            if player.state not in (PlayerStateEnum.BANNED, PlayerStateEnum.DISCONNECTED)
        )

    @cached_property
    def valid_num_players(self) -> bool:
        return MIN_NUM_PLAYERS <= self.active_players_count <= MAX_NUM_PLAYERS


class GameUpdateSchema(BaseModel, OneFieldSetMixin):
    state: GameStateEnum | None = None
    selected_player_id: int | None = Field(default=UnsetSentinel)
    selected_prompt_id: int | None = Field(default=UnsetSentinel)
    lead_state: LeadStateEnum | None = None
    update_players: dict[int, PlayerUpdateSchema] = Field(default_factory=dict)
    add_player_ids: list[int] = Field(default_factory=list)

    @field_validator("state")
    @classmethod
    def check_supplied_values_not_none(
        cls,
        value: int | list[int] | None,
        info: ValidationInfo,
    ) -> int | list[int]:
        return supplied_value_is_not_none(value, info)


class GameSessionShema(BaseModel):
    model_config = ConfigDict(frozen=True)

    game_id: int
    player_id: int
    is_lead: bool


class GamePayloadSchema(BaseModel):
    game: GameSchema


class GameEventSchema(BaseModel):
    name: str = "game.event"
    payload: BaseModel | None = None
