import logging
from app.bot import PriceBot

logger = logging.getLogger(__name__)

class BotAdapter:
    def __init__(self, client, bot: PriceBot):
        self.client = client
        self.bot = bot

    async def on_message(self, event, text: str) -> None:
        reply_text, photo = await self.bot.handle_text(text)
        try:
            if photo is not None:
                await self.client.send_photo(event, photo, caption="نرخ لحظه‌ای بازار")
            else:
                await self.client.send_text(event, reply_text)
        except Exception as e:
            logger.exception("send_failed", extra={"chat_id": event.chat_id})
            try:
                await event.reply(f"Send Error: {e}")
            except:
                pass
