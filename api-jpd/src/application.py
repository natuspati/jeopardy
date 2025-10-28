import logging

import socketio
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.responses import RedirectResponse

import api
from configs import override_external_loggers, settings
from errors import add_error_handlers
from lifespan import lifespan
from websocket import sio

override_external_loggers()

_logger = logging.getLogger(__name__)

fastapi_app = FastAPI(
    title=settings.name,
    version=settings.version,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

fastapi_app.include_router(api.router)


@fastapi_app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url=fastapi_app.url_path_for("get_swagger_documentation"))


add_error_handlers(fastapi_app)

socketio_app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

_logger.info(f"Finished setting application up, version: {settings.version}")
