import asyncio
from app.cache import TTLCache


def test_stale_fallback():
    async def scenario():
        cache = TTLCache(ttl_seconds=0)
        calls = {"n": 0}

        async def ok():
            calls["n"] += 1
            return "v1"

        async def fail():
            raise RuntimeError("upstream down")

        v, _, stale = await cache.get_or_fetch("k", ok)
        assert (v, stale) == ("v1", False)

        v, _, stale = await cache.get_or_fetch("k", fail)
        assert (v, stale) == ("v1", True)
        assert calls["n"] == 1

    asyncio.run(scenario())
