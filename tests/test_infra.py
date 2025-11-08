import pytest
import aiohttp
from http import HTTPStatus


pytestmark = pytest.mark.asyncio

async def test_healthcheck(api_base_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}/health") as resp:
            assert resp.status == HTTPStatus.OK
            data = await resp.json()
            assert data.get("status") == "ok"  # optional if your endpoint returns {"status": "ok"}
