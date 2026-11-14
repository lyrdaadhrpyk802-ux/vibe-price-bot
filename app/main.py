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
from botapi import VibeBot

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
            logger.info("cache_refreshed")
        except Exception:
            logger.exception("periodic_refresh_failed")
        await asyncio.sleep(interval)

async def run() -> None:
    setup_logging(settings.log_level)

    token = settings.bot_token.strip()
    if not token or ":" not in token:
        logger.error("VIBE_BOT_TOKEN is missing or invalid")
        raise SystemExit(1)

    service = await build_service()
    price_bot = PriceBot(service)
    refresh_task = asyncio.create_task(periodic_refresh(service, settings.cache_ttl_seconds))

    delay = 5
    try:
        while True:
            bot = VibeBot(token=token)
            adapter = BotAdapter(VibeBotAdapter(bot), price_bot)

            try:
                async with bot:
                    me = await bot.get_me()
                    bot_username = getattr(me, "username", "bot")
                    
                    async def handler(event):
                        text = event.raw_text or ""
                        
                        # Logic for Groups: Only reply if mentioned, replied to, or command
                        if event.is_group:
                            is_mentioned = f"@{bot_username}" in text
                            is_reply_to_me = False
                            if event.is_reply:
                                reply_msg = await event.get_reply_message()
                                if reply_msg and reply_msg.sender_id == me.id:
                                    is_reply_to_me = True
                            
                            if not (text.startswith("/") or is_mentioned or is_reply_to_me):
                                return

                        try:
                            await adapter.on_message(event.chat_id, text)
                        except Exception:
                            logger.exception("handler_failed")

                    bot.raw.add_event_handler(handler, events.NewMessage(incoming=True))

                    logger.info("bot_connected username=%s", bot_username)
                    await bot.run_until_disconnected()

                delay = 5

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
