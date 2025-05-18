from collections.abc import Sequence
from typing import Any

import pydantic

from jlib.errors.schema import SchemaValidationError
from jlib.types import schemas


def validate_json(
    data: str,
    schema: type[schemas.T],
) -> schemas.T:
    try:
        return schema.model_validate_json(data)
    except pydantic.ValidationError as error:
        raise SchemaValidationError(error) from error


def validate_model(
    data: Sequence | Any,
    schema: type[schemas.T],
) -> list[schemas.T] | schemas.T | None:
    if data is None:
        return None

    if isinstance(data, Sequence):
        return _validate_schemas(
            data=data,
            schema=schema,
        )

    return _validate_single_schema(
        data=data,
        schema=schema,
    )


def _validate_single_schema(
    data: Any,
    schema: type[schemas.T],
) -> schemas.T:
    try:
        return schema.model_validate(data, from_attributes=True)
    except pydantic.ValidationError as error:
        raise SchemaValidationError(error) from error


def _validate_schemas(
    data: Sequence,
    schema: type[schemas.T],
) -> list[schemas.T]:
    try:
        return [schema.model_validate(obj, from_attributes=True) for obj in data]
    except pydantic.ValidationError as error:
        raise SchemaValidationError(error) from error
