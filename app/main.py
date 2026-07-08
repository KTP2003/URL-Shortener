from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from app.api.routes.shortener import router
from app.db.dependencies import get_url_service
from app.services.url_service import URLService
from contextlib import asynccontextmanager

from app.db.session import engine
from app.models.url import Base

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
    url = await service.get_by_short_code(short_code)
    if not url:
        raise HTTPException(status_code=404, detail="Short code not found")
    return RedirectResponse(
        url.original_url,
        status_code=307,
    )
