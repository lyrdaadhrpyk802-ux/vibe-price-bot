ASSET_ALIASES = {
    "دلار": "usd", "دلار آمریکا": "usd", "usd": "usd", "dollar": "usd",
    "یورو": "eur", "eur": "eur", "euro": "eur",
    "پوند": "gbp", "gbp": "gbp", "pound": "gbp",
    "درهم": "aed", "aed": "aed", "dirham": "aed",
    "بیت کوین": "btc", "بیت‌کوین": "btc", "بیتکوین": "btc",
    "bitcoin": "btc", "btc": "btc",
    "اتریوم": "eth", "ethereum": "eth", "eth": "eth",
    "طلا": "gold_18k", "طلای ۱۸": "gold_18k", "طلای 18": "gold_18k",
    "gold": "gold_18k", "gold_18k": "gold_18k",
}

_SORTED_ALIASES = sorted(ASSET_ALIASES.items(), key=lambda kv: -len(kv[0]))
