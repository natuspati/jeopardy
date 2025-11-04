import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from socketio import ASGIApp
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

import api
from configs import override_external_loggers, settings
from constants import ONE_DAY_IN_SECONDS
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=ONE_DAY_IN_SECONDS,
)


app.include_router(api.router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url=app.url_path_for("get_swagger_documentation"))


add_error_handlers(app)

socket_app = ASGIApp(socketio_server=sio, other_asgi_app=app, socketio_path="ws")

_logger.info(f"Finished setting application up, version: {settings.version}")
