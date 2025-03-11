from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from jlib.errors.base import BaseServiceError


def add_error_handlers(app: FastAPI):
    app.add_exception_handler(Exception, _handle_uncaught_error)
    app.add_exception_handler(BaseServiceError, _handle_service_error)


async def _handle_uncaught_error(request: Request, exc: Exception):
    return ORJSONResponse(
        content={"detail": str(exc)},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def _handle_service_error(request: Request, exc: BaseServiceError):
    return ORJSONResponse(
        content={"detail": exc.detail},
        status_code=exc.status_code,
    )
