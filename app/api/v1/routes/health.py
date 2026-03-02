from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.ENV,
    }
