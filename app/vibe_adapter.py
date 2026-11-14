import logging

logger = logging.getLogger(__name__)


class VibeBotAdapter:
    """
    Wraps a vibegram VibeBot so it satisfies BotAdapter's client contract:
      await client.send_text(chat_id, text)
      await client.send_photo(chat_id, photo_io, caption="")
    """

    def __init__(self, bot):
        self.bot = bot

    async def send_text(self, chat_id, text: str) -> None:
        await self.bot.send_message(chat_id, text)

    async def send_photo(self, chat_id, photo, caption: str = "") -> None:
        data = photo.getvalue() if hasattr(photo, "getvalue") else photo
        await self.bot.send_photo(chat_id, data, caption=caption)
