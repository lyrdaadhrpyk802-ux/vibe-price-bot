import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class VibeBotAdapter:
    def __init__(self, bot):
        self.bot = bot

    async def send_text(self, chat_id, text: str) -> None:
        await self.bot.send_message(chat_id, text)

    async def send_photo(self, chat_id, photo: BytesIO, caption: str = "") -> None:
        photo.name = "price-card.png"
        await self.bot.send_file(chat_id, photo, caption=caption)
