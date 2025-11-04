import socketio

from configs import settings
from websocket.namespaces import GameNamespace

sio = socketio.AsyncServer(
    client_manager=socketio.AsyncRedisManager(url=str(settings.redis_url)),
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
)


sio.register_namespace(GameNamespace("/game"))
