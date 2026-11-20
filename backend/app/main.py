from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_services.core.config import settings
try:
    from app.api.voice import router as voice_router
    from app.database import close_database, init_database
except ModuleNotFoundError:
    from backend.app.api.voice import router as voice_router
    from backend.app.database import close_database, init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield
    close_database()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}