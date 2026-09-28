from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.repositories.url_repository import URLRepository
from app.services.url_service import URLService
from app.cache.url_cache import URLCache


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_url_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> URLRepository:

    return URLRepository(db)


async def get_url_cache() -> URLCache:
    return URLCache()


async def get_url_service(
    repository: Annotated[URLRepository, Depends(get_url_repository)],
    cache: Annotated[URLCache, Depends(get_url_cache)]
) -> URLService:

    return URLService(repository, cache)