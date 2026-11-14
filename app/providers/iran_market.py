from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx

from app.errors import InvalidPrice, ProviderError
from app.models import AssetPrice

BASE_URL = (
    "https://raw.githubusercontent.com/iran-market/"
    "iran-market.github.io/main/data/latest-toman.json"
)

WANTED = {
    "USD_IRR_FREE", "EUR_IRR_FREE", "GBP_IRR_FREE", "AED_IRR_FREE",
    "GOLD_18K_IRR",
}


def _extract_items(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        data = payload.get("data", [])
        return data if isinstance(data, list) else []
    return []


def _to_decimal(raw) -> Decimal:
    try:
        value = Decimal(str(raw))
    except (InvalidOperation, TypeError):
        raise InvalidPrice(f"unparseable price: {raw!r}")
    if value <= 0 or value > Decimal("1e15"):
        raise InvalidPrice(f"out-of-range price: {value}")
    return value


class IranMarketProvider:
    name = "iran-market"

    async def fetch(self) -> dict[str, AssetPrice]:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(BASE_URL)
            resp.raise_for_status()
            payload = resp.json()

        result: dict[str, AssetPrice] = {}
        for item in _extract_items(payload):
            symbol = item.get("symbol")
            if symbol not in WANTED:
                continue
            result[symbol] = AssetPrice(
                symbol=symbol,
                name_fa=item.get("name_fa", symbol),
                price=_to_decimal(item.get("price")),
                currency=item.get("currency", "IRT"),
                change_pct=float(item.get("change_pct") or 0),
                timestamp=datetime.now(timezone.utc),
                source=self.name,
                stale=bool(item.get("stale", False)),
            )

        if not result:
            raise ProviderError("Iran Market returned no usable symbols")
        return result
