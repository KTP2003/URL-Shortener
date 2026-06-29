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
