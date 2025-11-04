import backoff
from elasticsearch import AsyncElasticsearch, ConnectionError
from typing import Any, TypeVar, AsyncGenerator
from config.config import settings

T = TypeVar("T")

@backoff.on_exception(
    backoff.expo,                      # exponential backoff (1s, 2s, 4s, 8s, …)
    ConnectionError,                 # retry on ES connection errors
    max_time=60,                       # stop retrying after 60 seconds
    max_tries=5,                       # or after 5 attempts, whichever comes first
    jitter=backoff.full_jitter         # randomize delay to reduce thundering herd
)
async def get_elastic_client() -> AsyncGenerator[AsyncElasticsearch, Any]:
    client = AsyncElasticsearch(hosts=[settings.elk_url], verify_certs=False)
    try:
        yield client
    finally:
        await client.close()


class ElasticRepository:
    """Generic repository for Elasticsearch operations."""

    def __init__(self, es: AsyncElasticsearch, index: str, model: type[T]):
        self.es = es
        self.index = index
        self.model = model

    async def get_by_id(self, entity_id: str) -> T:
        result = await self.es.get(index=self.index, id=entity_id)
        return self.model(**result["_source"])

    async def search(self, body: dict[str, Any]) -> list[T]:
        resp = await self.es.search(index=self.index, body=body)
        return [self.model(**hit["_source"]) for hit in resp["hits"]["hits"]]
