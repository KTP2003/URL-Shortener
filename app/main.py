from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.routes.shortener import router
from app.db.dependencies import get_url_service
from app.db.redis import redis_client
from app.db.session import engine
from app.exceptions import URLShortenerException
from app.models.url import Base
from app.services.url_service import URLService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ponytail: create_all duplicates Alembic, but the initial migration only
    # ALTERs columns so it cannot build the schema from scratch. Drop this once
    # a real create_table migration exists.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await redis_client.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/{short_code}", response_class=RedirectResponse)
async def redirect_short_url(
    short_code: str,
    service: Annotated[URLService, Depends(get_url_service)],
) -> RedirectResponse:
    redirect = await service.resolve_short_code(short_code)

    return RedirectResponse(
        redirect.original_url,
        status_code=307,
    )

@app.exception_handler(URLShortenerException)
async def application_exception_handler(
    request: Request,
    exc: URLShortenerException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
    )
