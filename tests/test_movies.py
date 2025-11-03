import pytest
import aiohttp

pytestmark = pytest.mark.asyncio


async def test_list_movies_returns_json_array(api_base_url):
    """Check that /movies/ returns a list of movie objects."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/movies/") as resp:
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            data = await resp.json()
            assert isinstance(data, list)
            if data:  # only check fields if list is non-empty
                movie = data[0]
                assert "id" in movie
                assert "title" in movie
                assert "type" in movie


async def test_list_movies_with_query_params(api_base_url):
    """Verify filtering/sorting parameters work and return consistent responses."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/movies/", params={"limit": 5, "sort": "rating"}) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) <= 5


async def test_get_movie_by_id(api_base_url):
    """Ensure /movies/{id} returns a valid movie object."""
    async with aiohttp.ClientSession() as session:
        # Get one movie ID first
        async with session.get(f"{api_base_url}/movies/?limit=1") as resp:
            assert resp.status == 200
            data = await resp.json()
            if not data:
                pytest.skip("No movies available in index")
            movie_id = data[0]["id"]

        # Fetch the same movie by ID
        async with session.get(f"{api_base_url}/movies/{movie_id}") as resp:
            assert resp.status == 200
            movie = await resp.json()
            assert movie["id"] == movie_id
            assert "title" in movie
            assert "type" in movie


# async def test_get_movie_invalid_id_returns_422(api_base_url):
#     """Invalid UUID should trigger validation error (422)."""
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{api_base_url}/movies/not-a-valid-id") as resp:
#             assert resp.status == 422
#             error = await resp.json()
#             assert "detail" in error
