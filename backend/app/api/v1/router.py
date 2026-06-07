from fastapi import APIRouter
from app.api.v1.routes import auth, interview

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])