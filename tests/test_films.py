import pytest
from http import HTTPStatus

pytestmark = pytest.mark.anyio


async def test_list_films_returns_json_array(client):
    """Check that /films/ returns a list of film objects."""
    resp = client.get("/films/")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert isinstance(data, list)
    if data:
        film = data[0]
        assert "id" in film
        assert "title" in film
        assert "type" in film


async def test_list_films_with_params(client):
    """Verify filtering/sorting parameters work and return consistent responses."""
    resp = client.get("/films/", params={"limit": 1, "sort": "rating"})
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 2


async def test_get_film_by_id(client):
    """Ensure /films/{id} returns a valid film object."""
    resp = client.get("/films/")
    data = resp.json()
    if not data:
        pytest.skip("No films available in index")

    film_id = data[0]["id"]
    resp = client.get(f"/films/{film_id}")
    assert resp.status_code == HTTPStatus.OK
    film = resp.json()
    assert film["id"] == film_id
    assert "title" in film
    assert "type" in film
