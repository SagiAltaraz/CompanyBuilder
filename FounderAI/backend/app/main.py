"""
FounderAI — FastAPI application entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.postgres import get_pool, close_pool
from .db.redis_client import close_redis
from .routers import blueprints, ws, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB pool and create tables
    await get_pool()
    yield
    # Shutdown: clean up connections
    await close_pool()
    await close_redis()


app = FastAPI(
    title="FounderAI",
    description="Multi-agent AI platform for building company blueprints",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blueprints.router)
app.include_router(ws.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
