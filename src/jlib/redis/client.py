from redis.asyncio import Redis

from settings import settings

_REDIS_CLIENT = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_pass,
    socket_timeout=settings.redis_socket_timeout,
)


def get_redis_client() -> Redis:
    return _REDIS_CLIENT
