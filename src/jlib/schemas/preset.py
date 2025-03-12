from pydantic import Field

from jlib.schemas.base import BaseSchema
from jlib.schemas.category import CategorySchema
from jlib.schemas.pagination import PaginatedResponseSchema


class PresetSchema(BaseSchema):
    id: int
    name: str
    owner_id: int
    categories: list[CategorySchema] = Field(
        default_factory=list,
    )


class BasicPresetSchema(BaseSchema):
    id: int
    name: str
    owner_id: int


class PaginatedBasicPresetSchema(PaginatedResponseSchema[BasicPresetSchema]):
    pass
