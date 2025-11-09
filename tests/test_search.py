import pytest
from http import HTTPStatus

pytestmark = pytest.mark.anyio


async def test_search_films_returns_json_array(client):
    """Check that /search returns a list of film objects matching the query."""
    params = {"query": "Star", "page_number": 1, "page_size": 5}
    resp = client.get("/search", params=params)

    assert resp.status_code == HTTPStatus.OK, (
        f"Expected {HTTPStatus.OK}, got {resp.status_code}"
    )
    data = resp.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"

    if data:
        film = data[0]
        assert "id" in film
        assert "title" in film
        assert "description" in film
        assert "type" in film
        assert "rating" in film
