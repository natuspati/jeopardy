from jlib.errors.base import BaseServiceError


class DBSessionManagerClosedError(BaseServiceError):
    detail = "Database session manager is closed"


class DatabaseDetailError(BaseServiceError):
    def __init__(self, error: Exception):
        detail = f"Database error: type {type(error)}\nmessage: {error}"
        super().__init__(detail)


class MissingRequiredDataInDBError(BaseServiceError):
    detail = "Missing required data in database"
