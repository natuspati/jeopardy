from starlette.testclient import TestClient


def test_internal_health(client: TestClient):
    response = client.get("/api/internal/health")
    assert response.status_code == 200
