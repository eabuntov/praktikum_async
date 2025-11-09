import pytest
from http import HTTPStatus

pytestmark = pytest.mark.anyio


async def test_healthcheck(client):
    """Ensure /health endpoint responds correctly."""
    resp = client.get("/health")

    assert resp.status_code == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {resp.status_code}"

    # if the endpoint returns JSON like {"status": "ok"}
    data = resp.json()
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    assert data.get("status") == "ok", f"Expected status='ok', got {data}"
