import arabic_reshaper
from bidi.algorithm import get_display


def rtl(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))
