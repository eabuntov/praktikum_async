import json

import redis.asyncio as aioredis

from config.config import settings

CACHE_TTL = 300

redis = aioredis.from_url(f"redis://redis:{settings.redis_port}", decode_responses=True)

async def get_from_cache(key: str):
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None


async def set_to_cache(key: str, value, ttl: int = CACHE_TTL):
    await redis.set(key, json.dumps(value, default=str), ex=ttl)