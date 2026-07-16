from datetime import datetime

from pydantic import BaseModel, HttpUrl

class URLCreate(BaseModel):
    url: HttpUrl
    alias: str | None = None
    expires_at: datetime | None = None

class URLResponse(BaseModel):
    short_url: str
    short_code: str
    expires_at: datetime | None = None