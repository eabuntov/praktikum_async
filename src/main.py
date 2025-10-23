from fastapi import FastAPI
from api import routes

# --- FastAPI setup ---
app = FastAPI(title="Movies API with Elasticsearch")

app.include_router(routes.movies_router)
