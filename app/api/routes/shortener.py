from typing import Annotated
from fastapi import APIRouter, Depends
from app.schemas.url import URLCreate, URLResponse
from app.db.dependencies import get_url_service
from app.services.url_service import URLService
from app.core.config import settings

router = APIRouter(
    prefix="/urls",
    tags=["URL Shortener"]
)


@router.post("/shorten", response_model=URLResponse, status_code=201)
async def shorten_url(
    payload: URLCreate,
    service: Annotated[URLService, Depends(get_url_service)],
) -> URLResponse:
    '''Endpoint to shorten a URL. It accepts a URLCreate object, normalizes the URL, checks for existing entries, generates a unique short code if necessary, and returns the created or existing URL entry.'''
    url = await service.create_url(
        url = str(payload.url),
        alias = payload.alias if payload.alias is not None else None
    )
    return URLResponse(
        short_code=url.short_code,
        short_url=f"{settings.base_url.rstrip('/')}/{url.short_code}",
    )

