import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    value: Any
    fetched_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int = 1200):
        self.ttl_seconds = ttl_seconds
        self._entries: dict[str, CacheEntry] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock_for(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def get_or_fetch(
        self,
        key: str,
        loader: Callable[[], Awaitable[Any]],
    ) -> tuple[Any, float, bool]:
        entry = self._entries.get(key)
        now = time.time()
        if entry and now - entry.fetched_at < self.ttl_seconds:
            return entry.value, now - entry.fetched_at, False

        async with self._lock_for(key):
            entry = self._entries.get(key)
            now = time.time()
            if entry and now - entry.fetched_at < self.ttl_seconds:
                return entry.value, now - entry.fetched_at, False

            try:
                value = await loader()
            except Exception:
                if entry is not None:
                    logger.warning("serving_stale_cache", extra={"key": key})
                    return entry.value, now - entry.fetched_at, True
                raise

            self._entries[key] = CacheEntry(value=value, fetched_at=time.time())
            return value, 0.0, False
