from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import create_tables
from app.db.models import User, UserRole, Interview, InterviewAnswer  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await create_tables()
    yield
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Interview Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/ui")
async def serve_ui():
    return FileResponse("interview_ui.html")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}