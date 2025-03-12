from datetime import datetime

from pydantic import Field

from jlib.schemas.base import BaseSchema
from jlib.schemas.category import CategorySchema
from jlib.schemas.pagination import PaginatedResponseSchema
from settings import settings


def _generate_preset_name() -> str:
    current_time = datetime.now(settings.timezone).strftime("%Y-%m-%d %H:%M:%S")
    return f"Preset created at {current_time}"


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


class PresetCreateShowSchema(BaseSchema):
    name: str


class PresetCreateSchema(BaseSchema):
    name: str = Field(default_factory=_generate_preset_name)
    owner_id: int


class PaginatedBasicPresetSchema(PaginatedResponseSchema[BasicPresetSchema]):
    pass
