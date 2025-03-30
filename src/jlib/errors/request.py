from fastapi import status

from jlib.errors.base import BaseServiceError


class BadRequestError(BaseServiceError):
    detail = "Bad request"
    status_code = status.HTTP_400_BAD_REQUEST


class BadDependencyInjectionError(BaseServiceError):
    detail = "Bad dependency injection"
