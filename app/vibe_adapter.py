import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class VibeBotAdapter:
    def __init__(self, bot):
        self.bot = bot

    async def send_text(self, event, text: str) -> None:
        await event.reply(text)

    async def send_photo(self, event, photo: BytesIO, caption: str = "") -> None:
        photo.name = "price-card.png"
        await self.bot.send_file(event.chat_id, photo, caption=caption)
