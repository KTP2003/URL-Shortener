from pydantic import BaseModel, HttpUrl

class URLCreate(BaseModel):
    url: HttpUrl
    alias: str | None = None

class URLResponse(BaseModel):
    short_url: str
    short_code: str