import logging
from collections.abc import Sequence
from datetime import timedelta
from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import Depends
from sqlalchemy import Executable
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession

from configs import settings
from constants import UnsetSentinel
from errors.storage import COMMON_DB_ERRORS, DBError, RedisBaseError
from storages import RedisManager, get_db_session, get_redis_manager

_logger = logging.getLogger(__name__)


class RelationalRepoMixin:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ):
        self._manager = None
        self._session = session

    async def execute(
        self,
        query: Executable,
        params: _CoreAnyExecuteParams | None = None,
    ) -> Any:
        try:
            return await self._session.execute(query, params=params)
        except COMMON_DB_ERRORS as error:
            return self._handle_error(error, str(error))

    async def scalar(
        self,
        query: Executable,
        params: _CoreAnyExecuteParams | None = None,
    ) -> Any:
        try:
            return await self._session.scalar(query, params=params)
        except COMMON_DB_ERRORS as error:
            return self._handle_error(error, str(query))

    async def scalars(
        self,
        query: Executable,
        params: _CoreAnyExecuteParams | None = None,
    ) -> Sequence:
        try:
            result = await self._session.scalars(query, params=params)
        except COMMON_DB_ERRORS as error:
            return self._handle_error(error, str(query))
        return result.all()

    @classmethod
    def _handle_error(
        cls,
        error: DatabaseError,
        statement: str,
    ) -> Any:
        _logger.error(
            f"Database error, statement: {statement},\ntype: {type(error)},\nmessage: {error}",
        )
        raise DBError(f"Database error: {error}")


class RedisRepoMixin:
    NAME_SPACE: str = ""
    EXPIRATION: timedelta = timedelta(seconds=settings.redis_expiration_sec)

    def __init__(
        self,
        redis_manager: Annotated[RedisManager, Depends(get_redis_manager)],
    ):
        self._manger = redis_manager

    async def get(self, name: str, **kwargs) -> Any:
        key = self._create_key(name, **kwargs)
        async with self._manger.client() as client:
            try:
                return await client.get(key)
            except redis.RedisError as error:
                return self._handle_error(key, error=error)

    async def set(
        self,
        name: str,
        value: Any,
        expire: int | timedelta | type(UnsetSentinel) | None = UnsetSentinel,
        **kwargs,
    ) -> bool:
        key = self._create_key(name, **kwargs)
        expire = self.EXPIRATION if expire is UnsetSentinel else expire
        async with self._manger.client() as client:
            try:
                return await client.set(key, value, ex=expire)
            except redis.RedisError as error:
                return self._handle_error(key, error=error)

    async def delete(self, name: str, **kwargs) -> int:
        key = self._create_key(name, **kwargs)
        async with self._manger.client() as client:
            try:
                return await client.delete(key)
            except redis.RedisError as error:
                return self._handle_error(key, error=error)

    @classmethod
    def _create_key(cls, name: str, **kwargs) -> str:
        if kwargs:
            parts = [f"{k}={v}" for k, v in sorted(kwargs.items())]
            extra = ":".join(parts)
            return f"{cls.NAME_SPACE}:{name}:{extra}"
        return f"{cls.NAME_SPACE}:{name}"

    @classmethod
    def _handle_error(cls, *keys: str, error: redis.RedisError) -> Any:
        _logger.error(
            f"Redis error for keys={keys}, type={type(error)}, message={error}",
        )
        raise RedisBaseError(f"Redis error: {error}")
