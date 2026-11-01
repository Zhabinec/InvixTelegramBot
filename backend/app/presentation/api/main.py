
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.presentation.api.routes.products import router as products_router
from app.infrastructure.config import DatabaseSettings, MinioSettings
from app.infrastructure.database.connection import create_database
from app.infrastructure.storage.minio_image_storage import MinioImageStorage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine, session_factory = create_database(DatabaseSettings())
    image_storage = MinioImageStorage(MinioSettings())

    app.state.session_factory = session_factory
    app.state.image_storage = image_storage

    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="Telegram Shop API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(products_router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
