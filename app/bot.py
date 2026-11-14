import logging
from app.errors import AssetNotFound, InvalidPrice, ProviderError
from app.nlp.parser import parse_request
from app.rendering.card import make_price_card
from app.service import PriceService

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "دستورات قیمت‌گیری:\n"
    "- دلار، یورو، پوند، درهم\n"
    "- 2.5 دلار\n"
    "- قیمت بیت‌کوین، اتریوم\n"
    "- طلا"
)

class PriceBot:
    def __init__(self, service: PriceService):
        self.service = service

    async def handle_text(self, text: str) -> tuple[str, bytes | None]:
        if not text or text.strip() in {"/start", "/help", "help", "راهنما"}:
            return HELP_TEXT, None

        parsed = parse_request(text)
        if parsed is None:
            return ("متوجه نشدم. " + HELP_TEXT, None)

        try:
            result = await self.service.get(parsed.asset)
        except AssetNotFound:
            return ("این دارایی در منابع فعلی موجود نیست.", None)
        except Exception as e:
            logger.exception("price_fetch_failed")
            return (f"خطا در دریافت قیمت: {str(e)[:50]}", None)

        total = result.price * parsed.amount
        price_text = f"{total:,.0f}"

        NAMES = {
            "usd": "دلار آمریکا",
            "eur": "یورو",
            "gbp": "پوند انگلیس",
            "aed": "درهم امارات",
            "gold_18k": "طلا ۱۸ عیار",
            "btc": "بیت کوین",
            "eth": "اتریوم"
        }
        clean_title = NAMES.get(parsed.asset, result.name_fa)

        sign = "+" if (result.change_pct or 0) >= 0 else ""
        caption_text = (
            f"{clean_title} (بازار آزاد): {price_text} {result.currency}\n"
            f"تغییرات: {sign}{(result.change_pct or 0):.2f}%\n"
            f"بروزرسانی: {_age_text(result.age_seconds)}"
        )

        try:
            card = make_price_card(
                title=clean_title,
                price_text=price_text,
                unit=result.currency,
                change_pct=result.change_pct or 0.0,
                values=result.history,
                age_text=_age_text(result.age_seconds),
                source=result.symbol,
                is_stale=result.is_stale,
            )
            return caption_text, card
        except Exception:
            logger.exception("card_render_failed")
            return caption_text, None

def _age_text(seconds: float) -> str:
    minutes = int(seconds // 60)
    if minutes < 1:
        return "همین الان"
    if minutes < 60:
        return f"{minutes} دقیقه پیش"
    h, m = divmod(minutes, 60)
    return f"{h} ساعت و {m} دقیقه پیش"
