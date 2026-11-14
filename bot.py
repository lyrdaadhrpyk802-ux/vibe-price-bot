import asyncio
import os
import sys
import traceback
from telethon import events
from botapi import VibeBot

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[bot] error: VIBE_BOT_TOKEN is not set")
        sys.exit(1)

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
            print(f"[bot] connected as @{getattr(me, 'username', 'bot')}")

            @bot.raw.on(events.NewMessage(incoming=True))
            async def handler(event):
                text = (event.raw_text or "").strip()
                print(f"[bot] received: {text}")
                
                if text == "/ping":
                    await event.reply("pong")
                    return

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
