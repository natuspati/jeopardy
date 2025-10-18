from fastapi import status
from fastapi.testclient import TestClient

from configs import settings


async def test_internal_health(client: TestClient):
    resp = client.get("/api/health")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json().get("version") == settings.version
