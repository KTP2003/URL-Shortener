from sqlalchemy.orm import Session
from app.models.url import URL

class URLRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_url(self, url: URL) -> URL:
        self.session.add(url)
        self.session.commit()
        self.session.refresh(url)
        return url
    
    def get_by_short_code(self, short_code: str) -> URL | None:
        return self.session.query(URL).filter(URL.short_code == short_code).first()
    
    def get_by_original_url(self, original_url: str) -> URL | None:
        return self.session.query(URL).filter(URL.original_url == original_url).first()

    def get_normalised_url(self, normalised_url: str) -> URL | None:
        return self.session.query(URL).filter(URL.normalised_url == normalised_url).first()
