from fastapi import FastAPI

from app.api import user
from app.api import vectordb
from app.core.config import settings

app = FastAPI(title="RAG & SQL", version="0.1.0")

app.include_router(user.router)
app.include_router(vectordb.router)


