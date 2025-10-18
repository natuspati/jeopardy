from fastapi import status

from errors.base import BaseError


class BadRequestError(BaseError):
    detail = "Bad Request"
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(BaseError):
    detail = "Not Found"
    status_code = status.HTTP_404_NOT_FOUND


class InputValidationError(BaseError):
    detail = "Input validation error"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
