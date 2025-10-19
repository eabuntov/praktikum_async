from fastapi import HTTPException, Query
from typing import Optional, List

from src.main import app, INDEX_NAME, es, INDEX_GENRES, INDEX_PEOPLE
from src.models.models import FilmWork, Genre, Person


@app.get("/movies/{movie_id}", response_model=FilmWork)
async def get_movie(movie_id: str):
    """Get a single movie by ID."""
    try:
        result = await es.get(index=INDEX_NAME, id=movie_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Movie not found")

    return FilmWork(id=result["_id"], **result["_source"])


@app.get("/movies/", response_model=List[FilmWork])
async def list_movies(
    query: Optional[str] = Query(None, description="Search by title or description"),
    sort: Optional[str] = Query(None, description="Sort by field, e.g. rating or creation_date"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc"),
    min_rating: Optional[float] = Query(None, description="Filter by minimum rating"),
    max_rating: Optional[float] = Query(None, description="Filter by maximum rating"),
    type: Optional[str] = Query(None, description="Filter by movie type"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Search, filter, and sort movies."""
    must_clauses = []
    filter_clauses = []

    # Full-text search
    if query:
        must_clauses.append({
            "multi_match": {
                "query": query,
                "fields": ["title^2", "description"]
            }
        })

    # Rating filters
    if min_rating is not None or max_rating is not None:
        range_filter = {}
        if min_rating is not None:
            range_filter["gte"] = min_rating
        if max_rating is not None:
            range_filter["lte"] = max_rating
        filter_clauses.append({"range": {"rating": range_filter}})

    # Type filter
    if type:
        filter_clauses.append({"term": {"type.keyword": type}})

    # Query body
    body = {
        "query": {
            "bool": {
                "must": must_clauses or [{"match_all": {}}],
                "filter": filter_clauses
            }
        },
        "from": offset,
        "size": limit,
    }

    # Sorting
    if sort:
        body["sort"] = [{sort: {"order": sort_order}}]

    resp = await es.search(index=INDEX_NAME, body=body)

    results = [
        FilmWork(id=hit["_id"], **hit["_source"])
        for hit in resp["hits"]["hits"]
    ]

    return results


@app.get("/genres/{genre_id}", response_model=Genre)
async def get_genre(genre_id: str):
    """Get a single genre by ID."""
    try:
        result = await es.get(index=INDEX_GENRES, id=genre_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Genre not found")
    return Genre(id=result["_id"], **result["_source"])


@app.get("/genres/", response_model=List[Genre])
async def list_genres(
    query: Optional[str] = Query(None, description="Search by name or description"),
    sort: Optional[str] = Query(None, description="Sort by field, e.g. name or created"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List or search genres."""
    must = []
    if query:
        must.append({
            "multi_match": {"query": query, "fields": ["name^2", "description"]}
        })

    body = {
        "query": {"bool": {"must": must or [{"match_all": {}}]}},
        "from": offset,
        "size": limit,
    }

    if sort:
        body["sort"] = [{sort: {"order": sort_order}}]

    resp = await es.search(index=INDEX_GENRES, body=body)
    return [Genre(id=hit["_id"], **hit["_source"]) for hit in resp["hits"]["hits"]]


@app.get("/people/{person_id}", response_model=Person)
async def get_person(person_id: str):
    """Get a single person by ID."""
    try:
        result = await es.get(index=INDEX_PEOPLE, id=person_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Person not found")
    return Person(id=result["_id"], **result["_source"])


@app.get("/people/", response_model=List[Person])
async def list_people(
    query: Optional[str] = Query(None, description="Search by full name"),
    sort: Optional[str] = Query(None, description="Sort by field, e.g. full_name or created"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List or search people."""
    must = []
    if query:
        must.append({
            "multi_match": {"query": query, "fields": ["full_name"]}
        })

    body = {
        "query": {"bool": {"must": must or [{"match_all": {}}]}},
        "from": offset,
        "size": limit,
    }

    if sort:
        body["sort"] = [{sort: {"order": sort_order}}]

    resp = await es.search(index=INDEX_PEOPLE, body=body)
    return [Person(id=hit["_id"], **hit["_source"]) for hit in resp["hits"]["hits"]]


@app.on_event("shutdown")
async def shutdown_event():
    """Close Elasticsearch connection."""
    await es.close()

