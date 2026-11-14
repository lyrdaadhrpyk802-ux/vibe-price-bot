import logging

from app.errors import AssetNotFound, InvalidPrice, ProviderError
from app.nlp.parser import parse_request
from app.rendering.card import make_price_card
from app.service import PriceService

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "Ask prices like:\n"
    "- dollar\n- 2.5 dollar\n- bitcoin price\n- gold\n"
    "Supported: usd, eur, gbp, aed, gold_18k, btc, eth"
)


class PriceBot:
    def __init__(self, service: PriceService):
        self.service = service

    async def handle_text(self, text: str) -> tuple[str, bytes | None]:
        if not text or text.strip() in {"/start", "/help", "help"}:
            return HELP_TEXT, None

        parsed = parse_request(text)
        if parsed is None:
            return ("Not understood. " + HELP_TEXT, None)

        try:
            result = await self.service.get(parsed.asset)
        except AssetNotFound:
            return ("Asset not available in current sources. " + HELP_TEXT, None)
        except (ProviderError, InvalidPrice):
            logger.exception("price_fetch_failed")
            return ("Cannot fetch price right now. Try again later.", None)

        total = result.price * parsed.amount
        price_text = f"{total:,.0f}"

        try:
            card = make_price_card(
                title=result.name_fa,
                price_text=price_text,
                unit=result.currency,
                change_pct=result.change_pct or 0.0,
                values=result.history,
                age_text=_age_text(result.age_seconds),
                source=result.symbol,
                is_stale=result.is_stale,
            )
            return "", card
        except Exception:
            logger.exception("card_render_failed")
            stale_line = "\n[STALE DATA]" if result.is_stale else ""
            return (
                f"{result.name_fa}: {price_text} {result.currency}\n"
                f"Change: {(result.change_pct or 0):+.2f}%\n"
                f"Updated: {_age_text(result.age_seconds)}"
                f"{stale_line}",
                None,
            )


def _age_text(seconds: float) -> str:
    minutes = int(seconds // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"
    h, m = divmod(minutes, 60)
    return f"{h}h {m}m ago"
