from typing import Protocol
from app.models import AssetPrice


class PriceProvider(Protocol):
    name: str
    async def fetch(self) -> dict[str, AssetPrice]: ...
