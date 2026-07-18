from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse

from app.api.routes.shortener import router
from app.db.dependencies import get_url_service
from app.services.url_service import URLService
from contextlib import asynccontextmanager

from app.db.session import engine
from app.models.url import Base
from app.exceptions import URLShortenerException



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/{short_code}", response_class=RedirectResponse)
async def redirect_short_url(
    short_code: str,
    service: Annotated[URLService, Depends(get_url_service)],
) -> RedirectResponse:
    url = await service.resolve_short_code(short_code)
    
    return RedirectResponse(
        url.original_url,
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