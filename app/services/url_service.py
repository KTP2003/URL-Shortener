from app.repositories.url_repository import URLRepository
from app.models.url import URL
from app.utils.short_code import generate_short_code
from urllib.parse import urlparse

class URLService:
    def __init__(self, repository: URLRepository):
        self.repository = repository

    def _normalise_url(self, url: str) -> str:
        """Normalise the URL by ensuring it has a scheme and is in lowercase."""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url.rstrip('/').lower()
    
    def _generate_unique_short_code(self) -> str:
        """Generate a unique short code that doesn't already exist in the database."""
        while True:
            short_code = generate_short_code()
            if not self.repository.get_by_short_code(short_code):
                return short_code

    def create_url(self, url: str) -> URL:
        # 1. Normalize the URL
        # 2. Check if it already exists
        # 3. If yes, return existing short URL
        # 4. Generate a new short code
        # 5. Create URL model
        # 6. Save using repository
        # 7. Return response
        normalised_url = self._normalise_url(url)
        existing_url = self.repository.get_by_normalised_url(normalised_url)

        if existing_url:
            return existing_url
        else:
            short_code = self._generate_unique_short_code()
            new_url = URL(original_url=url, normalised_url=normalised_url, short_code=short_code)
            self.repository.create_url(new_url)
            return new_url

