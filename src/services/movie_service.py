import logging
from typing import Optional, List
from api.v1.caching import get_from_cache
from models.models import FilmWork
from repositories.elastic_repository import ElasticRepository

logger = logging.getLogger(__name__)

class MovieService:
    """Service handling movie search and retrieval."""

    def __init__(self, repo: ElasticRepository):
        self.repo = repo

    async def get_movie(self, movie_id: str) -> FilmWork:
        cache_key = f"movie:{movie_id}"
        cached = await get_from_cache(cache_key)
        if cached:
            return FilmWork(**cached)
        return await self.repo.get_by_id(movie_id)

    async def list_movies(
        self,
        query: Optional[str],
        sort: Optional[str],
        sort_order: str,
        min_rating: Optional[float] = 0.0,
        max_rating: Optional[float] = 10.0,
        type_: Optional[str] = "movie",
        limit: int = 10,
        offset: int = 0
    ) -> List[FilmWork]:
        cache_key = f"movies:list:{query}:{sort}:{sort_order}:{min_rating}:{max_rating}:{type_}:{limit}:{offset}"
        cached = await get_from_cache(cache_key)
        if cached:
            return [FilmWork(**doc) for doc in cached]

        must, filters = [], []

        if query:
            must.append({
                "multi_match": {"query": query, "fields": ["title^2", "description"]}
            })

        if min_rating is not None or max_rating is not None:
            range_filter = {}
            if min_rating is not None:
                range_filter["gte"] = min_rating
            if max_rating is not None:
                range_filter["lte"] = max_rating
            filters.append({"range": {"rating": range_filter}})

        if type_:
            filters.append({"term": {"type.keyword": type_}})

        body = {
            "query": {
                "bool": {"must": must or [{"match_all": {}}], "filter": filters}
            },
            "from": offset,
            "size": limit,
        }

        if sort:
            body["sort"] = [{sort: {"order": sort_order}}]

        logger.info("Executing movie search query.")
        return await self.repo.search(body)
