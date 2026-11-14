import re

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS  = "٠١٢٣٤٥٦٧٨٩"
ENGLISH_DIGITS = "0123456789"

_TRANSLATION = str.maketrans(
    PERSIAN_DIGITS + ARABIC_DIGITS,
    ENGLISH_DIGITS + ENGLISH_DIGITS,
)

_REPLACEMENTS = {
    "ي": "ی",
    "ى": "ی",
    "ك": "ک",
    "\u200c": " ",
    ",": "",
    "٬": "",
    "٫": ".",
}


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = text.translate(_TRANSLATION)
    for old, new in _REPLACEMENTS.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text)
