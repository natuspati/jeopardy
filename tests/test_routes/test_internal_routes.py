from starlette.testclient import TestClient

from jlib.db import DBManager


async def test_internal_health(client: TestClient, db_manager: DBManager):
    resp = client.get("/api/internal/health")
    assert resp.status_code == 200
