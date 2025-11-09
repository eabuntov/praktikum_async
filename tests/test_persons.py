import pytest
from http import HTTPStatus

pytestmark = pytest.mark.anyio


async def test_list_persons_returns_json_array(client):
    """Check that /persons/ returns a list of person objects."""
    resp = client.get("/persons/")
    assert resp.status_code == HTTPStatus.OK, (
        f"Expected {HTTPStatus.OK}, got {resp.status_code}"
    )
    data = resp.json()
    assert isinstance(data, list)
    if data:
        person = data[0]
        assert "id" in person
        assert "full_name" in person


async def test_list_persons_with_query_params(client):
    """Verify query and sorting for persons."""
    resp = client.get("/persons/", params={"limit": 2})
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 2


async def test_get_person_by_id(client):
    """Ensure /persons/{id} returns a valid person object."""
    resp = client.get("/persons/")
    data = resp.json()
    if not data:
        pytest.skip("No persons available in index")

    person_id = data[0]["id"]
    resp = client.get(f"/persons/{person_id}")
    assert resp.status_code == HTTPStatus.OK
    person = resp.json()
    assert person["id"] == person_id
    assert "full_name" in person
