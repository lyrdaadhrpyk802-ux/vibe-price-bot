from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.errors import ProviderError
from app.models import AssetPrice

URL = "https://api.coingecko.com/api/v3/simple/price"
_COINS = {"bitcoin": ("BTC", "بیت‌کوین"), "ethereum": ("ETH", "اتریوم")}


class CoinGeckoProvider:
    name = "coingecko"

    async def fetch(self) -> dict[str, AssetPrice]:
        params = {
            "ids": ",".join(_COINS),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(URL, params=params)
            if resp.status_code == 429:
                raise ProviderError("CoinGecko rate limited (429)")
            resp.raise_for_status()
            data = resp.json()

        result: dict[str, AssetPrice] = {}
        for cg_id, (symbol, name_fa) in _COINS.items():
            block = data.get(cg_id)
            if not block or "usd" not in block:
                continue
            result[symbol] = AssetPrice(
                symbol=symbol,
                name_fa=name_fa,
                price=Decimal(str(block["usd"])),
                currency="USD",
                change_pct=float(block.get("usd_24h_change") or 0),
                timestamp=datetime.now(timezone.utc),
                source=self.name,
            )

        if not result:
            raise ProviderError("CoinGecko returned no usable coins")
        return result
