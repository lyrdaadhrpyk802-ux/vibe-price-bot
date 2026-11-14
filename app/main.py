import asyncio
import logging

from telethon import events

from app.adapter import BotAdapter
from app.bot import PriceBot
from app.cache import TTLCache
from app.config import settings
from app.logging_config import setup_logging
from app.providers.coingecko import CoinGeckoProvider
from app.providers.fallback import FallbackChain
from app.providers.iran_market import IranMarketProvider
from app.service import PriceService
from app.vibe_adapter import VibeBotAdapter

logger = logging.getLogger(__name__)


async def build_service() -> PriceService:
    cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)
    iran_chain = FallbackChain([IranMarketProvider()])
    crypto_chain = FallbackChain([CoinGeckoProvider()])
    return PriceService(cache, iran_chain, crypto_chain)


async def periodic_refresh(service: PriceService, interval: int = 1200) -> None:
    """Pre-warm cache every `interval` seconds."""
    while True:
        try:
            await service._iran_all()
            await service._crypto_all()
            logger.info("cache_refreshed")
        except Exception:
            logger.exception("periodic_refresh_failed")
        await asyncio.sleep(interval)


async def run() -> None:
    setup_logging(settings.log_level)

    # --- validate config ------------------------------------------------
    token = settings.bot_token.strip()
    if not token:
        logger.error("BOT_TOKEN is empty - set it via env or GitHub Secrets")
        raise SystemExit(1)
    if ":" not in token:
        logger.error("BOT_TOKEN format looks wrong (expected <id>:<hash>)")
        raise SystemExit(1)

    try:
        from botapi import VibeBot  # noqa: F401  (import-check only)
    except ImportError:
        logger.error("vibegram is not installed - run: pip install vibegram")
        raise SystemExit(1)

    # --- build domain objects once --------------------------------------
    service = await build_service()
    price_bot = PriceBot(service)
    refresh_task = asyncio.create_task(
        periodic_refresh(service, settings.cache_ttl_seconds)
    )

    delay = 5
    try:
        while True:
            bot = VibeBot(token=token)
            adapter = BotAdapter(VibeBotAdapter(bot), price_bot)

            try:
                async with bot:
                    # handler closes over this iteration's adapter
                    async def handler(event):
                        try:
                            await adapter.on_message(
                                event.chat_id, event.raw_text or ""
                            )
                        except Exception:
                            logger.exception("handler_failed")

                    bot.raw.add_event_handler(
                        handler, events.NewMessage(incoming=True)
                    )

                    me = await bot.get_me()
                    logger.info(
                        "bot_connected username=%s id=%s",
                        getattr(me, "username", "-"),
                        getattr(me, "id", "?"),
                    )

                    await bot.run_until_disconnected()

                delay = 5  # clean exit -> reset backoff

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("bot_connection_failed")
                await asyncio.sleep(delay)
                delay = min(delay * 2, 300)

    finally:
        refresh_task.cancel()
        try:
            await refresh_task
        except (asyncio.CancelledError, Exception):
            pass


if __name__ == "__main__":
    asyncio.run(run())
