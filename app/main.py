import asyncio
import logging

from app.adapter import BotAdapter
from app.bot import PriceBot
from app.cache import TTLCache
from app.config import settings
from app.logging_config import setup_logging
from app.providers.coingecko import CoinGeckoProvider
from app.providers.fallback import FallbackChain
from app.providers.iran_market import IranMarketProvider
from app.service import PriceService

logger = logging.getLogger(__name__)


async def build_service() -> PriceService:
    cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)
    iran_chain = FallbackChain([IranMarketProvider()])
    crypto_chain = FallbackChain([CoinGeckoProvider()])
    return PriceService(cache, iran_chain, crypto_chain)


async def periodic_refresh(service: PriceService, interval: int = 1200) -> None:
    while True:
        try:
            await service._iran_all()
            await service._crypto_all()
        except Exception:
            logger.exception("periodic_refresh_failed")
        await asyncio.sleep(interval)


async def run() -> None:
    """
    Production entrypoint.
    TODO: initialize your Vibe client here and wire events to adapter.on_message.
    """
    setup_logging(settings.log_level)
    service = await build_service()
    bot = PriceBot(service)

    # client = await make_client()
    # adapter = BotAdapter(client, bot)
    # asyncio.create_task(periodic_refresh(service, settings.cache_ttl_seconds))
    # await client.run_forever(on_message=adapter.on_message)

    logger.error("bot framework not configured - use `python -m app.demo` for testing")
    raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(run())
