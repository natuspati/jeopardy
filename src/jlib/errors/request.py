from jlib.errors.base import BaseServiceError
from fastapi import status


class BadRequestError(BaseServiceError):
    detail = "Bad request"
    status_code = status.HTTP_400_BAD_REQUEST
