import json
import os

import aioredis

CACHE_TTL = 300
REDIS_PORT = os.getenv("REDIS_PORT")

redis = aioredis.from_url(f"redis://redis:{REDIS_PORT}", decode_responses=True)

async def get_from_cache(key: str):
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None


async def set_to_cache(key: str, value, ttl: int = CACHE_TTL):
    await redis.set(key, json.dumps(value, default=str), ex=ttl)