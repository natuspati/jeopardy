from fastapi import status

from jlib.errors.base import BaseServiceError


class GameFlowError(BaseServiceError):
    detail = "Game flow error"


class WrongActionError(GameFlowError):
    detail = "Wrong action"
    status_code = status.HTTP_400_BAD_REQUEST
