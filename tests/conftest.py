import logging
import sys

import pytest
from unittest.mock import AsyncMock
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

sys.path.append("/opt/app/src")
from services.film_service import FilmService
from services.genre_service import GenreService
from services.person_service import PersonService
from repositories.elastic_repository import ElasticRepository


# ------------------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


# ------------------------------------------------------------------------------
# Shared Repository Mock
# ------------------------------------------------------------------------------
@pytest.fixture
def mock_repo():
    """Mock of ElasticRepository with async methods for general use."""
    repo = AsyncMock(spec=ElasticRepository)

    # Unified mocked behavior
    repo.get_by_id.side_effect = lambda id_: {
        "id": id_,
        "title": f"Mock Film {id_}",
        "description": "Mocked description",
        "type": "movie",
        "rating": 8.1,
        "name": f"Mock Genre {id_}",
        "full_name": f"Mock Person {id_}",
    }

    repo.search.return_value = [
        {
            "id": "1",
            "title": "Mock Film 1",
            "description": "Desc 1",
            "type": "movie",
            "rating": 8.1,
            "name": "Mock Genre 1",
            "full_name": "Mock Person 1",
        },
        {
            "id": "2",
            "title": "Mock Film 2",
            "description": "Desc 2",
            "type": "movie",
            "rating": 7.4,
            "name": "Mock Genre 2",
            "full_name": "Mock Person 2",
        },
    ]
    return repo


# ------------------------------------------------------------------------------
# Cache Mock
# ------------------------------------------------------------------------------
@pytest.fixture
def mock_cache(monkeypatch):
    """Patch get_from_cache to always return None to skip Redis."""

    async def fake_get_from_cache(_):
        return None

    monkeypatch.setattr("services.film_service.get_from_cache", fake_get_from_cache)
    monkeypatch.setattr("services.genre_service.get_from_cache", fake_get_from_cache)
    monkeypatch.setattr("services.person_service.get_from_cache", fake_get_from_cache)


# ------------------------------------------------------------------------------
# Service Fixtures
# ------------------------------------------------------------------------------
@pytest.fixture
def film_service(mock_repo):
    return FilmService(repo=mock_repo)


@pytest.fixture
def genre_service(mock_repo):
    return GenreService(repo=mock_repo)


@pytest.fixture
def person_service(mock_repo):
    return PersonService(repo=mock_repo)


# ------------------------------------------------------------------------------
# FastAPI Client Fixture (for integration-like tests)
# ------------------------------------------------------------------------------
@pytest.fixture
async def client(mock_cache, film_service, genre_service, person_service):
    """Create a FastAPI test app with mocked dependencies for all services."""
    app = FastAPI()

    # Dependency overrides
    def get_film_service() -> FilmService:
        return film_service

    def get_genre_service() -> GenreService:
        return genre_service

    def get_person_service() -> PersonService:
        return person_service

    # ----------------------- FILM ENDPOINTS -----------------------
    @app.get("/films/{film_id}")
    async def get_film(film_id: str, service: FilmService = Depends(get_film_service)):
        return await service.get_film(film_id)

    @app.get("/films/")
    async def list_films(service: FilmService = Depends(get_film_service)):
        return await service.list_films()

    @app.get("/search")
    async def search_films(
        query: str,
        page_number: int = 1,
        page_size: int = 10,
        service: FilmService = Depends(get_film_service),
    ):
        return await service.search_films(query, page_number, page_size)

    # ----------------------- GENRE ENDPOINTS -----------------------
    @app.get("/genres/{genre_id}")
    async def get_genre(
        genre_id: str, service: GenreService = Depends(get_genre_service)
    ):
        return await service.get_genre(genre_id)

    @app.get("/genres/")
    async def list_genres(service: GenreService = Depends(get_genre_service)):
        return await service.list_genres(
            sort=None, sort_order="asc", limit=10, offset=0
        )

    # ----------------------- PERSON ENDPOINTS -----------------------
    @app.get("/persons/{person_id}")
    async def get_person(
        person_id: str, service: PersonService = Depends(get_person_service)
    ):
        return await service.get_person(person_id)

    @app.get("/persons/")
    async def list_persons(service: PersonService = Depends(get_person_service)):
        return await service.list_people(
            sort=None, sort_order="asc", limit=10, offset=0
        )

    # ----------------------- HEALTHCHECK -----------------------
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    with TestClient(app) as client:
        yield client
