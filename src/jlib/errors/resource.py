from fastapi import status

from jlib.errors.base import BaseServiceError


class ResourceNotFoundError(BaseServiceError):
    detail = "Resource not found"
    status_code = status.HTTP_404_NOT_FOUND


class ResourceExistsError(BaseServiceError):
    detail = "Resource already exists"
    status_code = status.HTTP_409_CONFLICT
