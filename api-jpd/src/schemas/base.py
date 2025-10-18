from datetime import datetime
from typing import Annotated, Any, Self

from pydantic import AfterValidator, model_validator
from pydantic_core.core_schema import ValidationInfo

from errors.request import InputValidationError


def _remove_time_zone(value: datetime) -> datetime:
    if value.tzinfo is not None:
        value = value.replace(tzinfo=None)
    return value


NoTZDateTime = Annotated[datetime, AfterValidator(_remove_time_zone)]


class OneFieldSetMixin:
    @model_validator(mode="after")
    def check_search_fields_set(self) -> Self:
        if not self.model_fields_set:
            raise InputValidationError("At least one field must be set.")
        return self


def supplied_value_is_not_none(value: Any, info: ValidationInfo) -> Any:
    if value is None:
        raise ValueError(f"Field {info.field_name} cannot be None.")
    return value
