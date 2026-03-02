from fastapi import FastAPI
from app.core.config import get_settings
from app.core.middleware import register_middleware
from app.api.v1 import router as v1_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

register_middleware(app)

app.include_router(v1_router)
