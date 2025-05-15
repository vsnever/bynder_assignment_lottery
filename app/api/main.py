from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routers import user, lottery, ballot
from app.core.config import settings
from app.core.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Bynder lottery service API.",
    lifespan=lifespan
)

# Health check endpoint
@app.get("/health", tags=["Health"])
@app.get("/ping", tags=["Health"])
def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(user.router)
app.include_router(lottery.router)
app.include_router(ballot.router)
