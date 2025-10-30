from pydantic import BaseModel, field_validator

from constants import MAX_CATEGORIES_IN_LOBBY, MIN_CATEGORIES_IN_LOBBY
from enums.lobby import LobbyStateEnum
from schemas.base import NoTZDateTime


class BaseLobbySchema(BaseModel):
    id: int
    host_id: int
    state: LobbyStateEnum
    created_at: NoTZDateTime


class LobbyCreatePublicSchema(BaseModel):
    category_ids: list[int]

    @field_validator("category_ids")
    @classmethod
    def check_number_of_categories(cls, category_ids: list[int]) -> list[int]:
        if len(category_ids) != len(set(category_ids)):
            raise ValueError("Categories are not unique")

        if not (MIN_CATEGORIES_IN_LOBBY <= len(category_ids) <= MAX_CATEGORIES_IN_LOBBY):
            raise ValueError(
                "Category count should be between "
                f"{MIN_CATEGORIES_IN_LOBBY} and {MAX_CATEGORIES_IN_LOBBY}",
            )
        return category_ids


class LobbyCreateSchema(LobbyCreatePublicSchema):
    host_id: int
    state: LobbyStateEnum = LobbyStateEnum.CREATED


class LobbySearchSchema(BaseModel):
    host_id: int | None = None
    state: LobbyStateEnum = LobbyStateEnum.CREATED
    created_at: NoTZDateTime | None = None
