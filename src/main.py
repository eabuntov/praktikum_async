from contextlib import asynccontextmanager
import sys
sys.path.append("/opt")
from fastapi import FastAPI
from api.routes import movies_router, shutdown_elastic

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event handler
    yield
    # Shutdown event handler
    await shutdown_elastic()

app = FastAPI(title="Movies API with Elasticsearch", lifespan=lifespan)

app.include_router(movies_router)
