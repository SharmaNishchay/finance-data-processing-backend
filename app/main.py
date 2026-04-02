from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine
from app.models.base import Base
from app.routers import dashboard, records, users
from app.services.bootstrap import ensure_default_admin

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            await ensure_default_admin(session)
    except Exception as exc:  # pragma: no cover
        logger.warning("Database startup initialization skipped: %s", exc)
    yield


app = FastAPI(
    title="Finance Data Processing and Access Control Backend",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)
