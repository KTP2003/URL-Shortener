from datetime import datetime, timezone

from fastapi import HTTPException
from app.exceptions import AliasAlreadyExistsError, InvalidAliasError, InvalidExpirationError
from app.models.url import URL
from app.repositories.url_repository import URLRepository
from app.utils.alias import validate_alias
from app.utils.short_code import generate_short_code


class URLService:
    def __init__(self, repository: URLRepository):
        self.repository = repository

    def _normalise_url(self, url: str) -> str:
        """Normalise the URL by ensuring it has a scheme and is in lowercase."""
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        return url.rstrip("/").lower()
    
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
        normalised_url = self._normalise_url(url)
        existing_url = await self.repository.get_by_normalised_url(normalised_url)

        self._validate_expiration(expires_at)

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

        new_url = URL(original_url=url, normalised_url=normalised_url, short_code=short_code)
        return await self.repository.create_url(new_url)

    async def get_by_short_code(self, short_code: str) -> URL | None:
        return await self.repository.get_by_short_code(short_code)

