import asyncio
import os
import sys
import time
import traceback
from telethon import events
from botapi import VibeBot

# Import the modules created earlier
from app.bot import PriceBot
from app.cache import TTLCache
from app.providers.coingecko import CoinGeckoProvider
from app.providers.fallback import FallbackChain
from app.providers.iran_market import IranMarketProvider
from app.service import PriceService

LAST_REQUEST = {}
COOLDOWN_SECONDS = 5

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[bot] error: VIBE_BOT_TOKEN is not set")
        sys.exit(1)

    # Initialize Price Service
    print("[bot] Initializing Price Service...")
    service = PriceService(
        TTLCache(ttl_seconds=1200), # 20 minutes cache
        FallbackChain([IranMarketProvider()]),
        FallbackChain([CoinGeckoProvider()])
    )
    price_bot = PriceBot(service)

    while True:
        bot = VibeBot(token=token)
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
                text = (event.raw_text or "").strip()
                print(f"[bot] received: {text}")
                
                if text == "/ping":
                    await event.reply("pong")
                    return

                # Anti-spam check
                user_id = event.sender_id
                now = time.time()
                if user_id in LAST_REQUEST:
                    elapsed = now - LAST_REQUEST[user_id]
                    if elapsed < COOLDOWN_SECONDS:
                        remaining = int(COOLDOWN_SECONDS - elapsed)
                        await event.reply(f"لطفاً {remaining} ثانیه دیگر تلاش کنید.")
                        return
                LAST_REQUEST[user_id] = now

                # Group Logic
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
                    # Process text using PriceBot
                    reply_text, photo = await price_bot.handle_text(text)
                    
                    if photo is not None:
                        photo.name = "price-card.png"
                        await bot.send_file(event.chat_id, photo, caption=reply_text)
                    else:
                        await event.reply(reply_text)
                        
                except Exception as e:
                    print(f"[bot] error processing: {e}")
                    traceback.print_exc()
                    await event.reply(f"Error: {str(e)[:150]}")

            print("[bot] listening for messages")
            await bot.run_until_disconnected()
        except Exception as e:
            print(f"[bot] crashed: {e}")
            traceback.print_exc()
            await asyncio.sleep(10)
        finally:
            try:
                await bot.disconnect()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
