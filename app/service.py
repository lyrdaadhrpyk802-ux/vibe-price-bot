from dataclasses import dataclass
from decimal import Decimal

from app.errors import AssetNotFound
from app.models import AssetPrice


@dataclass
class PriceResult:
    symbol: str
    name_fa: str
    price: Decimal
    currency: str
    change_pct: float | None
    history: list[float]
    age_seconds: float
    is_stale: bool


_IRAN_MARKET_MAP = {
    "usd": "USD_IRR_FREE",
    "eur": "EUR_IRR_FREE",
    "gbp": "GBP_IRR_FREE",
    "aed": "AED_IRR_FREE",
    "gold_18k": "GOLD_18K_IRR",
}

_CRYPTO = {"btc", "eth"}


class PriceService:
    def __init__(self, cache, iran_chain, crypto_chain):
        self.cache = cache
        self.iran_chain = iran_chain
        self.crypto_chain = crypto_chain
        self._history: dict[str, list[float]] = {}

    async def _iran_all(self):
        return await self.cache.get_or_fetch("iran-market", self.iran_chain.fetch)

    async def _crypto_all(self):
        return await self.cache.get_or_fetch("crypto", self.crypto_chain.fetch)

    def _record_history(self, symbol: str, price: Decimal) -> list[float]:
        values = self._history.setdefault(symbol, [])
        if not values or values[-1] != float(price):
            values.append(float(price))
            if len(values) > 48:
                del values[:-48]
        return list(values)

    async def get(self, asset: str) -> PriceResult:
        if asset in _IRAN_MARKET_MAP:
            data, age, stale = await self._iran_all()
            item = data.get(_IRAN_MARKET_MAP[asset])
            if item is None:
                raise AssetNotFound(f"{asset} not in iran-market payload")

            if item.currency == "IRR":
                display_price = item.price / Decimal("10")
                display_currency = "IRT"
            else:
                display_price = item.price
                display_currency = item.currency

            return PriceResult(
                symbol=asset,
                name_fa=item.name_fa,
                price=display_price,
                currency=display_currency,
                change_pct=item.change_pct,
                history=self._record_history(asset, display_price),
                age_seconds=age,
                is_stale=stale or item.stale,
            )

        if asset in _CRYPTO:
            data, age, stale = await self._crypto_all()
            item = data.get(asset.upper())
            if item is None:
                raise AssetNotFound(f"{asset} not in crypto payload")

            iran_data, _, _ = await self._iran_all()
            usd = iran_data.get("USD_IRR_FREE")
            if usd is None:
                raise AssetNotFound("USD rate unavailable")
            usd_toman = usd.price if usd.currency == "IRT" else usd.price / Decimal("10")
            toman_price = (item.price * usd_toman).quantize(Decimal("1"))

            return PriceResult(
                symbol=asset,
                name_fa=item.name_fa,
                price=toman_price,
                currency="IRT",
                change_pct=item.change_pct,
                history=self._record_history(asset, toman_price),
                age_seconds=age,
                is_stale=stale,
            )

        raise AssetNotFound(f"unsupported asset: {asset}")
