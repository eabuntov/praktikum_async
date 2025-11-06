import pytest
import aiohttp

pytestmark = pytest.mark.asyncio


async def test_search_films_returns_json_array(api_base_url):
    """Check that /films/search returns a list of film objects."""
    params = {"query": "Star", "page_number": 1, "page_size": 5}

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/search", params=params) as resp:
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            data = await resp.json()

            assert isinstance(data, list), f"Expected list, got {type(data)}"

            if data:
                film = data[0]
                # Validate basic structure
                assert "id" in film, "Film object should have 'id'"
                assert "title" in film, "Film object should have 'title'"
                assert "description" in film, "Film object should have 'description'"
                assert "type" in film, "Film object should have 'type'"
                assert "rating" in film, "Film object should have 'rating'"


async def test_search_films_with_no_results(api_base_url):
    """Ensure the endpoint returns an empty list for unknown queries."""
    params = {"query": "nonexistentfilmquery", "page_number": 1, "page_size": 5}

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/search", params=params) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) == 0, f"Expected empty list, got {len(data)}"
