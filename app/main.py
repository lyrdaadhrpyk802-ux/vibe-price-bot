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

async def run() -> None:
    setup_logging(settings.log_level)

    token = settings.bot_token.strip()
    if not token or ":" not in token:
        logger.error("VIBE_BOT_TOKEN is missing or invalid")
        raise SystemExit(1)

    service = await build_service()
    price_bot = PriceBot(service)

    while True:
        bot = VibeBot(token=token)
        adapter = BotAdapter(VibeBotAdapter(bot), price_bot)
        print("[bot] connecting...")

        try:
            connected = await bot.connect()
            if not connected:
                print("[bot] connect returned False, retrying in 10s...")
                await asyncio.sleep(10)
                continue

            me = await bot.get_me()
            bot_username = getattr(me, "username", "bot")
            print(f"[bot] connected as @{bot_username}")

            @bot.raw.on(events.NewMessage(incoming=True))
            async def handler(event):
                text = event.raw_text or ""
                print(f"[bot] received: {text}")
                
                if text == "/ping":
                    await event.reply("pong")
                    return

                # Logic for Groups: Only reply if mentioned, replied to, or command
                if event.is_group:
                    is_mentioned = f"@{bot_username}" in text
                    is_reply_to_me = False
                    if event.is_reply:
                        try:
                            reply_msg = await event.get_reply_message()
                            if reply_msg and reply_msg.sender_id == me.id:
                                is_reply_to_me = True
                        except Exception:
                            pass
                    
                    if not (text.startswith("/") or is_mentioned or is_reply_to_me):
                        return

                try:
                    await adapter.on_message(event, text)
                except Exception as e:
                    print(f"[bot] handler error: {e}")
                    try:
                        await event.reply(f"Error: {str(e)[:100]}")
                    except:
                        pass

            print("[bot] listening for messages")
            await bot.run_until_disconnected()
            
        except asyncio.TimeoutError:
            break
        except Exception as exc:
            print(f"[bot] connection crashed: {exc}")
            await asyncio.sleep(10)
        finally:
            try:
                await bot.disconnect()
            except Exception:
                pass

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
