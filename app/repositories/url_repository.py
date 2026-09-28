from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL


class URLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_url(self, url: URL) -> URL:
        self.session.add(url)
        await self.session.flush()
        await self.session.refresh(url)
        return url

    async def get_by_short_code(self, short_code: str) -> URL | None:
        result = await self.session.execute(
            select(URL).where(URL.short_code == short_code)
        )
        return result.scalar_one_or_none()

    async def get_by_normalised_url(self, normalised_url: str) -> URL | None:
        result = await self.session.execute(
            select(URL).where(URL.normalised_url == normalised_url)
        )
        return result.scalar_one_or_none()

    async def record_redirect(self, short_code: str) -> None:
        """Bump click stats without loading the row, so a cache hit costs one query."""
        await self.session.execute(
            update(URL)
            .where(URL.short_code == short_code)
            .values(
                click_count=URL.click_count + 1,
                last_accessed_at=datetime.now(timezone.utc),
            )
        )

    async def delete_url(self, url: URL) -> None:
        await self.session.delete(url)
