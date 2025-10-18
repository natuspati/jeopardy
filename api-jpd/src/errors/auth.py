from fastapi import status

from errors.base import BaseError


class UnauthorizedError(BaseError):
    detail = "Unauthorized access"
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(BaseError):
    detail = "Forbidden"
    status_code = status.HTTP_403_FORBIDDEN
