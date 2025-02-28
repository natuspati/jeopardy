from fastapi import status

from jlib.errors.base import BaseServiceError


class UnauthorizedError(BaseServiceError):
    detail = "Unauthorized access"
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(BaseServiceError):
    detail = "Forbidden access"
    status_code = status.HTTP_403_FORBIDDEN


class ImproperTokenError(BaseServiceError):
    detail = "Invalid token"
    status_code = status.HTTP_401_UNAUTHORIZED
