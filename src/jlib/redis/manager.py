from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from jlib.redis.client import get_redis_client
from settings import settings


class RedisManager:
    def __init__(self, client: Annotated[Redis, Depends(get_redis_client)]):
        self._client = client
        self._ns = settings.redis_namespace
        self._match = f"{self._ns}*"
        self._expire = timedelta(minutes=settings.redis_default_expiration_time)
        self._empty_value = settings.redis_empty_value

    def add_namespace(self, ns: str) -> None:
        self._ns += f"{ns}_"
        self._match = f"{self._ns}*"

    async def get(self, **filters: str | int) -> str | int | float | None:
        value = await self._client.get(name=self._create_name(**filters))
        if value == self._empty_value:
            return None
        return value

    async def select(self, offset: int, limit: int) -> list[str | int | float]:
        count = 0
        results = []
        async for key in self._client.scan_iter(
            match=self._match,
            count=limit + offset,
        ):
            if count < offset:
                count += 1
                continue
            result = await self._client.get(key)
            if result == self._empty_value:
                continue
            results.append(result)
            if len(results) >= limit:
                break
        return results

    async def set(
        self,
        value: str | int | float | None,
        expire: timedelta | int | None = None,
        **filters: str | int,
    ) -> None:
        """
        Set value to redis.

        :value: value to set
        :expire: expiration time in seconds or timedelta
        :filters: filters to use for key creation
        :return:
        """
        value = self._empty_value if value is None else value
        await self._client.set(
            name=self._create_name(**filters),
            value=value,
            ex=expire or self._expire,
        )

    async def delete(self, **filters: str | int) -> None:
        await self._client.delete(self._create_name(**filters))

    def _create_name(self, **filters: str | int) -> str:
        name = f"{self._ns}:"
        for key, value in filters.items():
            name += f"{key}={value},"
        return name.rstrip(",")
