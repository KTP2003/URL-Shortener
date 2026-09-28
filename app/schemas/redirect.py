from datetime import datetime

from pydantic import BaseModel


class RedirectData(BaseModel):
    short_code: str
    original_url: str
    expires_at: datetime | None = None