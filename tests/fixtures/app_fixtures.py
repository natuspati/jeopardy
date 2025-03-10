import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncConnection

from application import app
from jlib.db import DBManager
from jlib.db.utilities import get_db_manager
from models.base import meta
from settings import settings

_logger = logging.getLogger(__name__)


@pytest.fixture
async def db_manager():
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
async def test_app(db_manager: DBManager) -> FastAPI:
    app.dependency_overrides[get_db_manager] = lambda: db_manager
    return app


@pytest.fixture
async def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
