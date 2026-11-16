"""
AI Resume Screening & Candidate Ranking Platform - FastAPI Backend
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()  # must run before modules that read env vars at import time

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

import models  # noqa: E402,F401  (registers all ORM models on Base.metadata)
from database.connection import engine, Base  # noqa: E402
from routers import auth, candidates, jobs, ranking, analytics  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    upload_dir = os.getenv("UPLOAD_DIR", "uploads/resumes")
    os.makedirs(upload_dir, exist_ok=True)
    yield


app = FastAPI(
    title="AI Resume Screening Platform",
    description="Production-quality resume screening and candidate ranking API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(ranking.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI Resume Screening Platform API"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {"status": "healthy", "version": "1.0.0"}
