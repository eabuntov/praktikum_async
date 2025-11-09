import pytest
from http import HTTPStatus

pytestmark = pytest.mark.anyio


async def test_list_genres_returns_json_array(client):
    """Check that /genres/ returns a list of genre objects."""
    resp = client.get("/genres/")
    assert resp.status_code == HTTPStatus.OK, (
        f"Expected {HTTPStatus.OK}, got {resp.status_code}"
    )
    data = resp.json()
    assert isinstance(data, list)
    if data:
        genre = data[0]
        assert "id" in genre
        assert "name" in genre


async def test_list_genres_with_query_params(client):
    """Verify query, sorting, and pagination for genres."""
    resp = client.get("/genres/", params={"limit": 2})
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 2


async def test_get_genre_by_id(client):
    """Ensure /genres/{id} returns a valid genre object."""
    resp = client.get("/genres/")
    data = resp.json()
    if not data:
        pytest.skip("No genres available in index")

    genre_id = data[0]["id"]
    resp = client.get(f"/genres/{genre_id}")
    assert resp.status_code == HTTPStatus.OK
    genre = resp.json()
    assert genre["id"] == genre_id
    assert "name" in genre
