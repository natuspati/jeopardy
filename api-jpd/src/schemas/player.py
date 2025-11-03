from pydantic import BaseModel, ValidationInfo, field_validator

from enums.player import LeadStateEnum, PlayerStateEnum
from schemas.base import OneFieldSetMixin, supplied_value_is_not_none


class PlayerSchema(BaseModel):
    id: int
    username: str
    state: PlayerStateEnum = PlayerStateEnum.CONNECTED
    score: int = 0


class LeadSchema(BaseModel):
    id: int
    username: str
    state: LeadStateEnum = LeadStateEnum.CONNECTED


class PlayerUpdateSchema(BaseModel, OneFieldSetMixin):
    state: PlayerStateEnum | None = None
    score: int | None = None

    @field_validator("state", "score")
    @classmethod
    def check_supplied_values_not_none(
        cls,
        value: int | list[int] | None,
        info: ValidationInfo,
    ) -> int | list[int]:
        return supplied_value_is_not_none(value, info)
