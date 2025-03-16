import logging
from typing import AsyncIterator

import fakeredis
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncConnection

from application import app
from jlib.db import DBManager
from jlib.db.utilities import get_db_manager
from jlib.redis.client import get_redis_client
from models.base import meta
from settings import settings

_logger = logging.getLogger(__name__)


@pytest.fixture
async def db_manager() -> AsyncIterator[DBManager]:
    test_db_mngr = DBManager(
        db_url=settings.db_url,
        db_echo=settings.db_echo,
        db_echo_pool=settings.db_echo_pool,
        db_isolation_level=settings.db_isolation_level,
        db_expire_on_commit=settings.db_expire_on_commit,
    )
    async with test_db_mngr.connect() as conn:
        conn: AsyncConnection
        await conn.run_sync(meta.create_all)
    yield test_db_mngr
    await test_db_mngr.close()


@pytest.fixture
async def redis_client() -> AsyncIterator[fakeredis.FakeAsyncRedis]:
    async with fakeredis.FakeAsyncRedis(
        # host=settings.redis_host,
        port=settings.redis_port,
    ) as r_client:
        yield r_client


@pytest.fixture
async def test_app(
    db_manager: DBManager,
    redis_client: fakeredis.FakeAsyncRedis,
) -> FastAPI:
    app.dependency_overrides[get_db_manager] = lambda: db_manager
    app.dependency_overrides[get_redis_client] = lambda: redis_client
    return app


@pytest.fixture
async def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
