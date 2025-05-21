from fastapi import status

from jlib.errors.base import BaseServiceError


class GameFlowError(BaseServiceError):
    detail = "Game flow error"
    status_code = status.HTTP_400_BAD_REQUEST


class WrongActionError(GameFlowError):
    detail = "Wrong action"


class InvalidGameStateError(BaseServiceError):
    detail = "Invalid game state"
