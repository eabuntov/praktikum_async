from fastapi import FastAPI
from elasticsearch import AsyncElasticsearch

# --- FastAPI setup ---
app = FastAPI(title="Movies API with Elasticsearch")

# --- Elasticsearch connection ---
es = AsyncElasticsearch(hosts=["http://localhost:9200"])
INDEX_NAME = "movies"