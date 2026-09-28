"""Standalone checks for the cache read-through path. Run: python test_url_service.py"""
import asyncio
import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/test")
os.environ.setdefault("BASE_URL", "http://localhost:8000")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.exceptions import URLExpiredError, URLNotFoundError
from app.models.url import URL
from app.schemas.redirect import RedirectData
from app.services.url_service import URLService


class FakeRepo:
    def __init__(self, rows=()):
        self.rows = {r.short_code: r for r in rows}
        self.lookups = 0
        self.redirects = []

    async def get_by_short_code(self, short_code):
        self.lookups += 1
        return self.rows.get(short_code)

    async def record_redirect(self, short_code):
        self.redirects.append(short_code)

    async def delete_url(self, url):
        del self.rows[url.short_code]


class FakeCache:
    def __init__(self):
        self.store = {}

    async def get(self, short_code):
        return self.store.get(short_code)

    async def set(self, data):
        self.store[data.short_code] = data

    async def delete(self, short_code):
        self.store.pop(short_code, None)


def row(code="abc", url="http://example.com/AbC", expires_at=None):
    return URL(original_url=url, normalised_url=url, short_code=code, expires_at=expires_at)


async def main():
    # normalise: host lowercased, path case preserved, trailing slash dropped
    svc = URLService(FakeRepo(), FakeCache())
    assert svc._normalise_url("HTTP://Example.COM/AbC/") == "http://example.com/AbC"
    assert svc._normalise_url("example.com") == "http://example.com"
    assert svc._normalise_url("http://a.com/x") != svc._normalise_url("http://a.com/X")

    # miss -> DB, populates cache; hit -> no second DB lookup
    repo, cache = FakeRepo([row()]), FakeCache()
    svc = URLService(repo, cache)
    assert (await svc.resolve_short_code("abc")).original_url == "http://example.com/AbC"
    assert repo.lookups == 1 and "abc" in cache.store
    await svc.resolve_short_code("abc")
    assert repo.lookups == 1, "cache hit still queried the database"
    assert repo.redirects == ["abc", "abc"], "clicks must be counted on cache hits too"

    # unknown code
    try:
        await URLService(FakeRepo(), FakeCache()).resolve_short_code("nope")
        raise AssertionError("expected URLNotFoundError")
    except URLNotFoundError:
        pass

    # a cached entry that has since expired must not be served
    cache = FakeCache()
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    await cache.set(RedirectData(short_code="old", original_url="http://e.com", expires_at=past))
    try:
        await URLService(FakeRepo(), cache).resolve_short_code("old")
        raise AssertionError("expected URLExpiredError")
    except URLExpiredError:
        pass

    # delete invalidates the cache
    repo, cache = FakeRepo([row()]), FakeCache()
    svc = URLService(repo, cache)
    await svc.resolve_short_code("abc")
    await svc.delete_url("abc")
    assert cache.store == {}, "delete left a stale cache entry"

    print("all checks passed")


asyncio.run(main())
