from fastapi import FastAPI
from starlette.requests import Request
from starlette.websockets import WebSocket

from jlib.errors.request import BadDependencyInjectionError


def get_app(request: Request = None, websocket: WebSocket = None) -> FastAPI:
    if request:
        return request.app
    elif websocket:
        return websocket.app
    raise BadDependencyInjectionError("No request or websocket")
