from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from app.cache.url_cache import URLCache
from app.core.config import settings
from app.exceptions import (
    AliasAlreadyExistsError,
    InvalidAliasError,
    InvalidExpirationError,
    URLExpiredError,
    URLNotFoundError,
)
from app.models.url import URL
from app.repositories.url_repository import URLRepository
from app.schemas.redirect import RedirectData
from app.utils.alias import validate_alias
from app.utils.qr import generate_qr_code
from app.utils.short_code import generate_short_code


class URLService:
    def __init__(self, repository: URLRepository, cache: URLCache):
        self.repository = repository
        self.cache = cache

    def _normalise_url(self, url: str) -> str:
        """Normalise for deduplication: lowercase scheme and host, keep the path as-is."""
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https"):
            parts = urlsplit("http://" + url)

        return urlunsplit(
            (
                parts.scheme.lower(),
                parts.netloc.lower(),
                parts.path.rstrip("/"),
                parts.query,
                parts.fragment,
            )
        )

    def _validate_expiration(self, expires_at: datetime | None) -> None:
        """Validate that the expiration is in the future"""
        if expires_at is not None:
            if expires_at <= datetime.now(timezone.utc):
                raise InvalidExpirationError()

    async def _generate_unique_short_code(self) -> str:
        """Generate a unique short code that doesn't already exist in the database."""
        while True:
            short_code = generate_short_code()
            if not await self.repository.get_by_short_code(short_code):
                return short_code

    async def create_url(
            self,
            url: str,
            alias: str | None = None,
            expires_at: datetime | None = None
        ) -> URL:

        self._validate_expiration(expires_at)

        normalised_url = self._normalise_url(url)
        existing_url = await self.repository.get_by_normalised_url(normalised_url)

        if alias is not None:
            try:
                short_code = validate_alias(alias)
            except ValueError as ecx:
                raise InvalidAliasError(str(ecx)) from ecx

            existing_alias = await self.repository.get_by_short_code(short_code)
            if existing_alias:
                raise AliasAlreadyExistsError(alias)
        else:
            if existing_url:
                return existing_url

            short_code = await self._generate_unique_short_code()

        new_url = URL(original_url=url, normalised_url=normalised_url, short_code=short_code, expires_at=expires_at)
        return await self.repository.create_url(new_url)

    def _check_expired(self, expires_at: datetime | None) -> None:
        if expires_at and expires_at <= datetime.now(timezone.utc):
            raise URLExpiredError()

    async def _get_active_url(self, short_code: str) -> URL:
        url = await self.repository.get_by_short_code(short_code)
        if url is None:
            raise URLNotFoundError()
        self._check_expired(url.expires_at)
        return url

    async def resolve_short_code(self, short_code: str) -> RedirectData:
        data = await self.cache.get(short_code)

        if data is None:
            url = await self._get_active_url(short_code)
            data = RedirectData(
                short_code=url.short_code,
                original_url=url.original_url,
                expires_at=url.expires_at,
            )
            await self.cache.set(data)
        else:
            # A cached entry can outlive its expiry if expires_at was set after caching.
            self._check_expired(data.expires_at)

        await self.repository.record_redirect(short_code)
        return data

    async def delete_url(self, short_code: str) -> None:
        url = await self._get_active_url(short_code)
        await self.repository.delete_url(url)
        await self.cache.delete(short_code)

    async def get_qr_code(self, short_code: str) -> bytes:
        url = await self._get_active_url(short_code)
        short_url = f"{settings.base_url.rstrip('/')}/{url.short_code}"
        return generate_qr_code(short_url)
