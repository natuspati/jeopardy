from sqlalchemy.exc import (
    DataError,
    DBAPIError,
    IntegrityError,
    ProgrammingError,
    ResourceClosedError,
)

from errors.base import BaseError

COMMON_DB_ERRORS = (
    ProgrammingError,
    ResourceClosedError,
    IntegrityError,
    DataError,
    DBAPIError,
)


class DBError(BaseError):
    detail = "Database error"


class RedisBaseError(BaseError):
    detail = "Redis error"
