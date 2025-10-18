import contextlib
import logging
from collections.abc import AsyncIterator

import redis.asyncio as redis
from redis.exceptions import RedisError

from errors.storage import RedisBaseError
from schemas.storage import RedisConnectionSchema

_logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, conn_config: RedisConnectionSchema):
        self._config = conn_config
        self._client = redis.Redis(
            host=conn_config.host,
            port=conn_config.port,
            db=conn_config.db,
            password=conn_config.password,
            decode_responses=conn_config.decode_responses,
            socket_timeout=conn_config.socket_timeout,
            max_connections=conn_config.max_connections,
        )

    async def ping(self) -> bool:
        try:
            return await self._client.ping()
        except RedisError as error:
            _logger.error("Failed to ping Redis", exc_info=error)
            raise RedisBaseError(f"Redis ping failed: {error}") from error

    @contextlib.asynccontextmanager
    async def client(self) -> AsyncIterator[redis.Redis]:
        if self._client is None:
            raise RedisBaseError("Redis client not initialized")

        try:
            yield self._client
        except RedisError as error:
            _logger.exception("Redis operation failed", exc_info=error)
            raise RedisBaseError(f"Redis error: {error}") from error

    async def close(self) -> None:
        if self._client is not None:
            try:
                await self._client.close()
                await self._client.connection_pool.disconnect()
            except Exception as error:
                _logger.warning("Error closing Redis client", exc_info=error)
            finally:
                self._client = None
