import json

from app.core.config import settings
from app.db.redis import redis_client
from app.schemas.redirect import RedirectData


class URLCache:

    @staticmethod
    def _key(short_code: str) -> str:
        return f"url:{short_code}"

    @staticmethod
    async def get(short_code: str) -> RedirectData | None:
        key = URLCache._key(short_code)

        cached_value = await redis_client.get(key)

        if cached_value is None:
            return None

        return RedirectData.model_validate_json(cached_value)

    @staticmethod
    async def set(data: RedirectData) -> None:
        key = URLCache._key(data.short_code)

        await redis_client.set(
            key,
            data.model_dump_json(),
            ex=settings.cache_ttl,
        )

    @staticmethod
    async def delete(short_code: str) -> None:
        key = URLCache._key(short_code)

        await redis_client.delete(key)