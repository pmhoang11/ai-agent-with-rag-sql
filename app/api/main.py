from fastapi import FastAPI

from app.api import user, workspace, space, document, chatbot
from app.core.config import settings
from app.models.base import Base
from app.db.base import engine

app = FastAPI(title="RAG & SQL", version="0.1.0")

app.include_router(user.router)
app.include_router(workspace.router)
app.include_router(space.router)
app.include_router(document.router)
app.include_router(chatbot.router)

Base.metadata.create_all(bind=engine)
