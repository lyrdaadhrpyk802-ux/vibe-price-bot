from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class AssetPrice:
    symbol: str
    name_fa: str
    price: Decimal
    currency: str
    change_pct: Optional[float]
    timestamp: datetime
    source: str
    stale: bool = False
