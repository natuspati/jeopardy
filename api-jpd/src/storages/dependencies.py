from collections.abc import AsyncGenerator
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configs import settings
from schemas.storage import DBConnectionSchema, RedisConnectionSchema
from storages.redis import RedisManager
from storages.relational_db import DBManager

_DEFAULT_DB_CONN_CONFIG = DBConnectionSchema(
    echo=settings.db_echo,
    echo_pool=settings.db_echo_pool,
    isolation_level=settings.db_isolation_level,
    expire_on_commit=settings.db_expire_on_commit,
    rollback=settings.db_rollback,
    conn_pool_size=settings.db_conn_pool_size,
    conn_pool_recycle=settings.db_conn_pool_recycle,
)


_DEFAULT_REDIS_CONFIG = RedisConnectionSchema(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=settings.redis_decode_responses,
    socket_timeout=settings.redis_socket_timeout,
    max_connections=settings.redis_max_connections,
)

_default_db_manager = DBManager(
    db_url=settings.db_url,
    conn_config=_DEFAULT_DB_CONN_CONFIG,
)

_default_redis_manager = RedisManager(conn_config=_DEFAULT_REDIS_CONFIG)


def get_db_manager() -> DBManager:
    return _default_db_manager


async def get_db_session(
    db_manager: Annotated[DBManager, Depends(get_db_manager)],
) -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.session() as session:
        yield session


def get_redis_manager() -> RedisManager:
    return _default_redis_manager


async def get_redis_client(
    redis_manager: Annotated[RedisManager, Depends(get_redis_manager)],
) -> AsyncGenerator[redis.Redis, None]:
    async with redis_manager.client() as client:
        yield client
