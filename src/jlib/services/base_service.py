from typing import Any, Iterable, TypeVar

from pydantic import ValidationError

from jlib.errors.schema import SchemaValidationError
from jlib.schemas.base import BaseSchema

T = TypeVar("T", bound=BaseSchema)


class SchemaValidationServiceMixin:
    @classmethod
    def _validate(
        cls,
        data: Iterable | Any,
        schema: type[T],
    ) -> list[T] | T:
        if isinstance(data, Iterable):
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
        data: Iterable,
        schema: type[BaseSchema],
    ) -> list[BaseSchema]:
        try:
            return [schema.model_validate(obj, from_attributes=True) for obj in data]
        except ValidationError as error:
            raise SchemaValidationError(error) from error
