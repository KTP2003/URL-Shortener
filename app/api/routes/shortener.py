from typing import Annotated
from fastapi import APIRouter, Depends, Response
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

@router.delete("/{short_code}", status_code=204)
async def delete_url(
    short_code: str,
    service: Annotated[URLService, Depends(get_url_service)],
) -> None:
    '''Endpoint to delete a shortened URL.'''
    await service.delete_url(short_code)

@router.get("/qr/{short_code}", response_class=Response)
async def get_qr_code(
    short_code: str,
    service: Annotated[URLService, Depends(get_url_service)],
) -> Response:
    qr = await service.get_qr_code(short_code)
    return Response(content=qr, media_type="image/png")