from datetime import datetime, timezone
from sqlalchemy import select
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

    async def get_by_original_url(self, original_url: str) -> URL | None:
        result = await self.session.execute(
            select(URL).where(URL.original_url == original_url)
        )
        return result.scalar_one_or_none()

    async def get_by_normalised_url(self, normalised_url: str) -> URL | None:
        result = await self.session.execute(
            select(URL).where(URL.normalised_url == normalised_url)
        )
        return result.scalar_one_or_none()

    async def get_normalised_url(self, normalised_url: str) -> URL | None:
        return await self.get_by_normalised_url(normalised_url)

    async def record_redirect(self, url: URL) -> None:
        url.click_count += 1
        url.last_accessed_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(url)

    async def delete_url(self, url: URL) -> None:
        await self.session.delete(url)
        await self.session.commit()