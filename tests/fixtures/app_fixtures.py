import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from application import app
from scripts.migrations import apply_migrations


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    apply_migrations()


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)
