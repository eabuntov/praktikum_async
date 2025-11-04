import pytest
import aiohttp

pytestmark = pytest.mark.asyncio


async def test_list_films_returns_json_array(api_base_url):
    """Check that /films/ returns a list of film objects."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/films/") as resp:
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            data = await resp.json()
            assert isinstance(data, list)
            if data:  # only check fields if list is non-empty
                film = data[0]
                assert "id" in film
                assert "title" in film
                assert "type" in film


async def test_list_films_with_params(api_base_url):
    """Verify filtering/sorting parameters work and return consistent responses."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/films/", params={"limit": 5, "sort": "rating"}) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) <= 5


async def test_get_film_by_id(api_base_url):
    """Ensure /films/{id} returns a valid film object."""
    async with aiohttp.ClientSession() as session:
        # Get one film ID first
        async with session.get(f"{api_base_url}/films/?limit=1") as resp:
            assert resp.status == 200
            data = await resp.json()
            if not data:
                pytest.skip("No films available in index")
            film_id = data[0]["id"]

        # Fetch the same film by ID
        async with session.get(f"{api_base_url}/films/{film_id}") as resp:
            assert resp.status == 200
            film = await resp.json()
            assert film["id"] == film_id
            assert "title" in film
            assert "type" in film


# async def test_get_film_invalid_id_returns_422(api_base_url):
#     """Invalid UUID should trigger validation error (422)."""
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{api_base_url}/films/not-a-valid-id") as resp:
#             assert resp.status == 422
#             error = await resp.json()
#             assert "detail" in error
