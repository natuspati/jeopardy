import logging

import socketio
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.responses import RedirectResponse

import api
from configs import override_external_loggers, settings
from errors import add_error_handlers
from lifespan import lifespan
from websocket.server import sio

override_external_loggers()

_logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.name,
    version=settings.version,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

app.include_router(api.router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url=app.url_path_for("get_swagger_documentation"))


add_error_handlers(app)

socket_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app, socketio_path="ws")

_logger.info(f"Finished setting application up, version: {settings.version}")
