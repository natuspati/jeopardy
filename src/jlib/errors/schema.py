from fastapi import status

from jlib.errors.base import BaseServiceError


class AllFieldsUnsetValidationError(BaseServiceError):
    detail = "At least one field must be set"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class SchemaValidationError(BaseServiceError):
    detail = "Schema validation error"
