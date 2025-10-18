import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from application import app


@pytest.fixture
async def test_app() -> FastAPI:
    return app


@pytest.fixture
async def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
