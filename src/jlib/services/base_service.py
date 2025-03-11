from typing import Any, Sequence

from pydantic import ValidationError

from jlib.errors.schema import SchemaValidationError
from jlib.schemas.base import BaseSchema
from jlib.types.schemas import T


class SchemaValidationServiceMixin:
    @classmethod
    def _validate(
        cls,
        data: Sequence | Any,
        schema: type[T],
    ) -> list[T] | T:
        if isinstance(data, Sequence):
            return cls._validate_schemas(
                data=data,
                schema=schema,
            )

        return cls._validate_single_schema(
            data=data,
            schema=schema,
        )

    @classmethod
    def _validate_single_schema(
        cls,
        data: Any,
        schema: type[BaseSchema],
    ) -> BaseSchema:
        try:
            return schema.model_validate(data, from_attributes=True)
        except ValidationError as error:
            raise SchemaValidationError(error) from error

    @classmethod
    def _validate_schemas(
        cls,
        data: Sequence,
        schema: type[BaseSchema],
    ) -> list[BaseSchema]:
        try:
            return [schema.model_validate(obj, from_attributes=True) for obj in data]
        except ValidationError as error:
            raise SchemaValidationError(error) from error
