import re
from dataclasses import dataclass
from decimal import Decimal

from .normalize import normalize_text
from .aliases import _SORTED_ALIASES

_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


@dataclass
class ParsedRequest:
    asset: str
    amount: Decimal = Decimal("1")


def parse_request(text: str) -> ParsedRequest | None:
    text = normalize_text(text)

    for alias, asset in _SORTED_ALIASES:
        if alias not in text:
            continue
        prefix = text.split(alias, 1)[0].strip()
        m = _NUMBER_RE.search(prefix)
        amount = Decimal(m.group()) if m else Decimal("1")
        return ParsedRequest(asset=asset, amount=amount)

    return None
