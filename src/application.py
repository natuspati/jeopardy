from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

import api
from jlib.errors import add_error_handlers
from lifespan import lifespan
from settings import settings

app = FastAPI(
    title=settings.app_name,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.include_router(api.router)
add_error_handlers(app)
