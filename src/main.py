from contextlib import asynccontextmanager
import sys
sys.path.append("/opt")
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from api.v1.routes import movies_router, shutdown_elastic

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event handler
    yield
    # Shutdown event handler
    await shutdown_elastic()

app = FastAPI(title="Movies API with Elasticsearch", lifespan=lifespan)

app.include_router(movies_router)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Рендеринг домашней страницы"""
    movies = await get_movies()
    return templates.TemplateResponse("index.html", {"request": request, "movies": movies})

@app.get("/health", response_class=JSONResponse)
async def healthcheck():
    """
    Простой healthcheck.
    Returns 200 OK если приложение живо.
    """
    return {"status": "ok"}


async def get_movies():
    """Мок-фильмы для домашней страницы"""
    return {
        "Featured": ["Psycho", "Pride & Prejudice", "Catch Me If You Can", "Being John Malkovich"],
        "Popular": ["Fullmetal Alchemist: Brotherhood", "Breaking Bad", "Maniac", "Black Mirror"],
        "Comedies": ["Ocean’s Eleven", "Ocean’s Thirteen", "Back to the Future", "The Big Lebowski"],
    }
