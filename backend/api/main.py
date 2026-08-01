"""
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings_fastapi import settings
from core.logging_config import setup_logging
from core.redis_client import close_redis
from api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title="Banking Management System API",
    description="Production-grade RESTful Banking API built with FastAPI, PostgreSQL, Redis, Celery",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main router under /api
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "environment": settings.APP_ENV}
