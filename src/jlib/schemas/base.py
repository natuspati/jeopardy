from pydantic import BaseModel, model_validator

from jlib.errors.schema import AllFieldsUnsetValidationError


class BaseSchema(BaseModel):
    pass


class OneFieldSetSchemaMixin:
    @model_validator(mode="after")
    @classmethod
    def check_at_least_one_field_is_set(
        cls,
        validated_schema: BaseSchema,
    ) -> BaseSchema:
        """
        Check if schema has at least one field set.

        :param validated_schema: validated schema
        :return: schema with at least one field set
        """
        if not validated_schema.model_fields_set:
            raise AllFieldsUnsetValidationError()
        return validated_schema
