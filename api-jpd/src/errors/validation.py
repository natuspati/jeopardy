import pydantic
from pydantic_core import ErrorDetails

from errors.base import BaseError


class SQLModelValidationError(BaseError):
    detail = "Database data validation error"

    def __init__(self, error: pydantic.ValidationError):
        super().__init__()

        errors = error.errors(include_url=False)
        try:
            for err in errors:
                err["input"] = {
                    "table": err["input"].__table__.fullname,
                    "data": err["input"].to_dict(json=True),
                }
        except (KeyError, AttributeError):
            errors = str(errors)

        self.errors: str | list[ErrorDetails] = errors
