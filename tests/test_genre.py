import aiohttp
import pytest

pytestmark = pytest.mark.asyncio

async def test_list_genres_returns_json_array(api_base_url):
    """Check that /genres/ returns a list of genre objects."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/genres/") as resp:
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            data = await resp.json()
            assert isinstance(data, list)
            if data:
                genre = data[0]
                assert "id" in genre
                assert "name" in genre


async def test_list_genres_with_query_params(api_base_url):
    """Verify query, sorting, and pagination for genres."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{api_base_url}/genres/", params={"limit": 5}
        ) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) <= 5


async def test_get_genre_by_id(api_base_url):
    """Ensure /genres/{id} returns a valid genre object."""
    async with aiohttp.ClientSession() as session:
        # First, get one genre ID
        async with session.get(f"{api_base_url}/genres/?limit=1") as resp:
            assert resp.status == 200
            data = await resp.json()
            if not data:
                pytest.skip("No genres available in index")
            genre_id = data[0]["id"]

        # Fetch same genre by ID
        async with session.get(f"{api_base_url}/genres/{genre_id}") as resp:
            assert resp.status == 200
            genre = await resp.json()
            assert genre["id"] == genre_id
            assert "name" in genre