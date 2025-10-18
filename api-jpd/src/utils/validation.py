from collections.abc import Sequence

import pydantic

import schemas
from errors.validation import SQLModelValidationError
from models.base import BaseDBModel


def validate_model(
    data: Sequence[BaseDBModel] | BaseDBModel | None,
    dto: type[schemas.T],
) -> list[schemas.T] | schemas.T | None:
    if data is None:
        return None

    if isinstance(data, Sequence):
        return _validate_models(data=data, dto=dto)

    return _validate_model(data=data, dto=dto)


def _validate_model(
    data: BaseDBModel,
    dto: type[schemas.T],
) -> schemas.T:
    try:
        return dto.model_validate(data, from_attributes=True)
    except pydantic.ValidationError as error:
        raise SQLModelValidationError(error) from error


def _validate_models(
    data: Sequence[BaseDBModel],
    dto: type[schemas.T],
) -> list[schemas.T]:
    try:
        return [dto.model_validate(obj, from_attributes=True) for obj in data]
    except pydantic.ValidationError as error:
        raise SQLModelValidationError(error) from error
