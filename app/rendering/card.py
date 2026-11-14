from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .chart import draw_line_chart

FONT_DIR = Path(__file__).resolve().parent.parent.parent / "fonts"
FONT_REGULAR = FONT_DIR / "Vazirmatn-Regular.ttf"
FONT_BOLD = FONT_DIR / "Vazirmatn-Bold.ttf"


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _draw_text_right(draw, xy_right, text, font, fill):
    try:
        # Native Pillow RTL support (requires libraqm)
        bbox = draw.textbbox((0, 0), text, font=font, direction="rtl", language="fa")
        w = bbox[2] - bbox[0]
        x = xy_right[0] - w
        y = xy_right[1]
        draw.text((x, y), text, font=font, fill=fill, direction="rtl", language="fa")
    except Exception:
        # Fallback to manual reshaping if libraqm is not available
        import arabic_reshaper
        from bidi.algorithm import get_display
        rendered = get_display(arabic_reshaper.reshape(text))
        bbox = draw.textbbox((0, 0), rendered, font=font)
        w = bbox[2] - bbox[0]
        x = xy_right[0] - w
        y = xy_right[1]
        draw.text((x, y), rendered, font=font, fill=fill)


def make_price_card(
    *,
    title: str,
    price_text: str,
    unit: str,
    change_pct: float,
    values: list[float],
    age_text: str,
    source: str,
    is_stale: bool,
) -> BytesIO:
    W, H = 1200, 700
    bg     = (18, 24, 38)
    panel  = (29, 38, 58)
    white  = (245, 247, 250)
    muted  = (160, 174, 192)
    green  = (45, 210, 130)
    red    = (245, 90, 90)
    amber  = (240, 180, 60)

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    f_title = _font(FONT_BOLD, 48)
    f_price = _font(FONT_BOLD, 64)
    f_small = _font(FONT_REGULAR, 26)
    f_tiny  = _font(FONT_REGULAR, 22)

    draw.rounded_rectangle((40, 40, W - 40, H - 40), radius=28, fill=panel)

    _draw_text_right(draw, (W - 90, 90), title, f_title, white)
    _draw_text_right(draw, (W - 90, 190), price_text, f_price, white)
    _draw_text_right(draw, (W - 90, 280), unit, f_small, muted)

    change_color = green if change_pct >= 0 else red
    sign = "+" if change_pct >= 0 else ""
    _draw_text_right(draw, (W - 90, 340), f"{sign}{change_pct:.2f}%", f_small, change_color)

    if is_stale:
        _draw_text_right(draw, (600, 90), "داده قدیمی", f_tiny, amber)

    draw_line_chart(draw, values, (90, 450, W - 90, H - 140), color=change_color)

    _draw_text_right(draw, (600, H - 110), f"بروزرسانی: {age_text}", f_tiny, muted)
    _draw_text_right(draw, (W - 90, H - 110), f"منبع: {source}", f_tiny, muted)

    out = BytesIO()
    out.name = "price-card.png"
    img.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out
