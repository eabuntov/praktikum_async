from fastapi import APIRouter, Depends, HTTPException, Query
from elasticsearch import AsyncElasticsearch, NotFoundError
from typing import List, Optional

from config.config import settings
from models.models import FilmWork
from repositories.elastic_repository import ElasticRepository
from services.movie_service import MovieService

movies_router = APIRouter(prefix="/movies", tags=["movies"])

async def get_elastic_client() -> AsyncElasticsearch:
    """Dependency that provides a single Elasticsearch client."""
    client = AsyncElasticsearch(hosts=[settings.elk_url], verify_certs=False)
    try:
        yield client
    finally:
        await client.close()

def get_movie_service(es: AsyncElasticsearch = Depends(get_elastic_client)) -> MovieService:
    repo = ElasticRepository(es, index="movies", model=FilmWork)
    return MovieService(repo)

@movies_router.get("/{movie_id}", response_model=FilmWork)
async def get_movie(movie_id: str, service: MovieService = Depends(get_movie_service)):
    """Get a single movie by ID."""
    try:
        return await service.get_movie(movie_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Movie not found")

@movies_router.get("/", response_model=List[FilmWork])
async def list_movies(
    query: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    min_rating: Optional[float] = Query(None),
    max_rating: Optional[float] = Query(None),
    type: Optional[str] = Query(None, alias="type"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MovieService = Depends(get_movie_service),
):
    """Search, filter, and sort movies."""
    return await service.list_movies(query, sort, sort_order, min_rating, max_rating, type, limit, offset)
