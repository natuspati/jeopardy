import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from errors.base import BaseError
from errors.validation import SQLModelValidationError

_logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, _handle_uncaught_error)
    app.add_exception_handler(BaseError, _handle_base_error)
    app.add_exception_handler(SQLModelValidationError, _handle_base_error)


def handle_event_errors(
    *,
    emit_error: bool = True,
    return_value: Any = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to handle errors in Socket.IO event handlers.

    :param emit_error: Whether to emit error message to client
    :param return_value: Value to return on error
    :return: Value to return on error
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            self_arg = args[0] if args else None
            sid = args[1] if len(args) > 1 else kwargs.get("sid")

            try:
                return await func(*args, **kwargs)
            except BaseError as error:
                _logger.error(f"Expected error in {func.__name__}: {error.detail}")
                if emit_error and self_arg and sid:
                    await self_arg._emit_error(f"Error: {error.detail}", room=sid)
                return return_value
            except Exception as error:
                _logger.error(f"Uncaught error in {func.__name__}: {error}", exc_info=True)
                if emit_error and self_arg and sid:
                    await self_arg._emit_error("Internal server error", room=sid)
                return return_value

        return wrapper

    return decorator


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
