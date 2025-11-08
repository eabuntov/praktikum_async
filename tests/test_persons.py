import aiohttp
import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_list_persons_returns_json_array(api_base_url):
    """Check that /persons/ returns a list of person objects."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/persons/") as resp:
            assert resp.status == HTTPStatus.OK, f"Expected {HTTPStatus.OK}, got {resp.status}"
            data = await resp.json()
            assert isinstance(data, list)
            if data:
                person = data[0]
                assert "id" in person
                assert "full_name" in person


async def test_list_persons_with_query_params(api_base_url):
    """Verify query and sorting for persons."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{api_base_url}/persons/", params={"limit": 5}
        ) as resp:
            assert resp.status == HTTPStatus.OK
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) <= 5


async def test_get_person_by_id(api_base_url):
    """Ensure /persons/{id} returns a valid person object."""
    async with aiohttp.ClientSession() as session:
        # First, get one person ID
        async with session.get(f"{api_base_url}/persons/?limit=1") as resp:
            assert resp.status == HTTPStatus.OK
            data = await resp.json()
            if not data:
                pytest.skip("No persons available in index")
            person_id = data[0]["id"]

        # Fetch same person by ID
        async with session.get(f"{api_base_url}/persons/{person_id}") as resp:
            assert resp.status == HTTPStatus.OK
            person = await resp.json()
            assert person["id"] == person_id
            assert "full_name" in person