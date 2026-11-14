import logging
from app.bot import PriceBot

logger = logging.getLogger(__name__)


class BotAdapter:
    """
    Client contract:
        await client.send_text(chat_id, text)
        await client.send_photo(chat_id, photo_bytes, caption="")
    """
    def __init__(self, client, bot: PriceBot):
        self.client = client
        self.bot = bot

    async def on_message(self, chat_id: str, text: str) -> None:
        reply_text, photo = await self.bot.handle_text(text)
        try:
            if photo is not None:
                await self.client.send_photo(chat_id, photo, caption="Market price")
            else:
                await self.client.send_text(chat_id, reply_text)
        except Exception:
            logger.exception("send_failed", extra={"chat_id": chat_id})
