from fastapi import APIRouter
from backend.api import health, voice, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(voice.router, prefix="/api", tags=["voice"])
api_router.include_router(ui.router, tags=["ui"])
