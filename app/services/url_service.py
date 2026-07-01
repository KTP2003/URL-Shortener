from app.repositories.url_repository import URLRepository
from app.models.url import URL
from urllib.parse import urlparse

class URLService:
    def __init__(self, repository: URLRepository):
        self.repository = repository

    def _normalise_url(self, url: str) -> str:
        """Normalise the URL by ensuring it has a scheme and is in lowercase."""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url.rstrip('/').lower()

    #def create_url(self, url: str) -> URL:
        # 1. Normalize the URL
        # 2. Check if it already exists
        # 3. If yes, return existing short URL
        # 4. Generate a new short code
        # 5. Create URL model
        # 6. Save using repository
        # 7. Return response



