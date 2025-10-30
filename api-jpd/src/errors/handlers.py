import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from errors.base import BaseError
from errors.validation import SQLModelValidationError

_logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, _handle_uncaught_error)
    app.add_exception_handler(BaseError, _handle_base_error)
    app.add_exception_handler(SQLModelValidationError, _handle_base_error)


async def _handle_uncaught_error(request: Request, exc: Exception) -> ORJSONResponse:
    _log_error(request, str(exc))
    error_content = {"detail": BaseError.detail}
    return ORJSONResponse(
        content=error_content,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def _handle_base_error(request: Request, exc: BaseError) -> ORJSONResponse:
    _log_error(request, str(exc))
    error_content = {"detail": exc.detail}
    return ORJSONResponse(
        content=error_content,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def _handle_sql_model_validation_error(
    request: Request,
    exc: SQLModelValidationError,
) -> ORJSONResponse:
    _log_error(request, str(exc))
    error_content = {"detail": exc.detail, "errors": exc.errors}
    return ORJSONResponse(
        content=error_content,
        status_code=exc.status_code,
        headers=exc.headers,
    )


def _log_error(request: Request, error_description: str) -> None:
    error_msg = f"Error occurred: {request.method} {request.url}"

    request_cookies = request.cookies
    if request_cookies:
        error_msg += f"\nCookies: {request_cookies}"

    error_msg += f"\n{error_description}"
    _logger.error(error_msg)
