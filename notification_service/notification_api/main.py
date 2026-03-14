from fastapi import FastAPI
from v1.api import router
from db import engine
from models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification API")

app.include_router(router)
