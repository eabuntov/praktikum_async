from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from elasticsearch import AsyncElasticsearch

from config.config import settings
from repositories.elastic_repository import ElasticRepository
from services.movie_service import MovieService
from models.models import FilmWork

templates = Jinja2Templates(directory="templates")

home_router = APIRouter(tags=["home"])

async def get_elastic_client() -> AsyncElasticsearch:
    """Provides a shared Elasticsearch client for dependency injection."""
    client = AsyncElasticsearch(hosts=[settings.elk_url], verify_certs=False)
    try:
        yield client
    finally:
        await client.close()

def get_movie_service(es: AsyncElasticsearch = Depends(get_elastic_client)) -> MovieService:
    """Factory for MovieService."""
    repo = ElasticRepository(es, index="movies", model=FilmWork)
    return MovieService(repo)

@home_router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    service: MovieService = Depends(get_movie_service),
):
    """Render home page with movie data from Elasticsearch."""
    movies = await service.list_movies(
        query=None,
        sort="rating",
        sort_order="desc",
        limit=10,
        offset=0,
    )

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "movies": movies},
    )
