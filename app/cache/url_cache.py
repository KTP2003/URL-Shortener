from datetime import datetime, timezone
import logging

from redis.exceptions import RedisError

from app.core.config import settings
from app.db.redis import redis_client
from app.schemas.redirect import RedirectData

logger = logging.getLogger(__name__)


class URLCache:
    """Fails open: if Redis is unreachable, callers fall back to the database."""

    @staticmethod
    def _key(short_code: str) -> str:
        return f"url:{short_code}"

    @staticmethod
    async def get(short_code: str) -> RedirectData | None:
        try:
            cached_value = await redis_client.get(URLCache._key(short_code))
        except RedisError:
            logger.warning("cache get failed for %s", short_code, exc_info=True)
            return None

        if cached_value is None:
            return None

        return RedirectData.model_validate_json(cached_value)

    @staticmethod
    async def set(data: RedirectData) -> None:
        ttl = settings.cache_ttl
        if data.expires_at is not None:
            # Never outlive the URL itself, or we serve an expired redirect.
            seconds_left = int((data.expires_at - datetime.now(timezone.utc)).total_seconds())
            if seconds_left <= 0:
                return
            ttl = min(ttl, seconds_left)

        try:
            await redis_client.set(URLCache._key(data.short_code), data.model_dump_json(), ex=ttl)
        except RedisError:
            logger.warning("cache set failed for %s", data.short_code, exc_info=True)

    @staticmethod
    async def delete(short_code: str) -> None:
        try:
            await redis_client.delete(URLCache._key(short_code))
        except RedisError:
            logger.warning("cache delete failed for %s", short_code, exc_info=True)
