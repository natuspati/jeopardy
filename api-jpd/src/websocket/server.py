import socketio

from websocket.namespaces import GameNamespace

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
)


sio.register_namespace(GameNamespace("/game"))
