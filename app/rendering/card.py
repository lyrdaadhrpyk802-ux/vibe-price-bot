from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .chart import draw_area_chart

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONT_DIR = BASE_DIR / "fonts"
ASSETS_DIR = BASE_DIR / "assets"

FONT_REGULAR = FONT_DIR / "Vazirmatn-Regular.ttf"
FONT_BOLD = FONT_DIR / "Vazirmatn-Bold.ttf"

def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()

def _draw_text(draw, xy, text, font, fill, align="right", direction="rtl"):
    try:
        bbox = draw.textbbox((0, 0), text, font=font, direction=direction, language="fa" if direction=="rtl" else "en")
        w = bbox[2] - bbox[0]
        x = xy[0] - w if align == "right" else xy[0]
        draw.text((x, xy[1]), text, font=font, fill=fill, direction=direction, language="fa" if direction=="rtl" else "en")
    except Exception:
        import arabic_reshaper
        from bidi.algorithm import get_display
        rendered = get_display(arabic_reshaper.reshape(text)) if direction == "rtl" else text
        bbox = draw.textbbox((0, 0), rendered, font=font)
        w = bbox[2] - bbox[0]
        x = xy[0] - w if align == "right" else xy[0]
        draw.text((x, xy[1]), rendered, font=font, fill=fill)

def make_price_card(title, price_text, unit, change_pct, values, age_text, source, is_stale):
    W, H = 1200, 700
    
    # Determine background image
    bg_file = "default"
    if "دلار" in title or "یورو" in title or "پوند" in title:
        bg_file = "usd_bg.png"
    elif "طلا" in title:
        bg_file = "gold_bg.jpg"
    elif "بیت" in title:
        bg_file = "btc_bg.jpg"

    bg_path = ASSETS_DIR / bg_file
    
    # Fallback colors based on asset
    c1, c2 = (30, 41, 59), (15, 23, 42)
    if "دلار" in title:
        c1, c2 = (30, 58, 138), (153, 27, 27) # Blue & Red
    elif "طلا" in title:
        c1, c2 = (113, 63, 18), (250, 204, 21) # Brown & Gold
    elif "بیت" in title:
        c1, c2 = (124, 45, 18), (249, 115, 22) # Dark Orange

    bg = None
    if bg_path.exists():
        try:
            bg = Image.open(bg_path).convert("RGB")
            bg = bg.resize((W, H), Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(15))
            overlay = Image.new("RGB", (W, H), (0, 0, 0))
            bg = Image.blend(bg, overlay, 0.5)
        except Exception:
            bg = None

    if bg is None:
        # Create a beautiful mesh gradient as fallback
        bg = Image.new("RGB", (W, H), c1)
        draw_bg = ImageDraw.Draw(bg)
        draw_bg.ellipse((W//4, -200, W+200, H//2), fill=c2)
        draw_bg.ellipse((-200, H//2, W//2, H+200), fill=c1)
        bg = bg.filter(ImageFilter.GaussianBlur(100))

    img = bg.convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # White Card
    card_x0, card_y0, card_x1, card_y1 = 60, 60, W - 60, H - 60
    draw.rounded_rectangle((card_x0, card_y0, card_x1, card_y1), radius=40, fill=(255, 255, 255, 255))

    f_title = _font(FONT_BOLD, 48)
    f_price = _font(FONT_BOLD, 85)
    f_unit = _font(FONT_BOLD, 36)
    f_small = _font(FONT_REGULAR, 28)
    f_tiny  = _font(FONT_REGULAR, 20)

    # Title
    _draw_text(draw, (card_x1 - 60, 90), title, f_title, (30, 41, 59))
    
    # IRT Badge
    draw.rounded_rectangle((card_x0 + 50, 90, card_x0 + 150, 140), radius=25, fill=(240, 240, 240))
    _draw_text(draw, (card_x0 + 75, 98), "IRT", f_small, (100, 100, 100), direction="ltr", align="left")

    # Price (Moved IRT to the left of the price to avoid overlap)
    price_bbox = draw.textbbox((0, 0), price_text, font=f_price, direction="ltr")
    price_w = price_bbox[2] - price_bbox[0]
    price_x = card_x1 - 60 - price_w
    
    draw.text((price_x, 170), price_text, font=f_price, fill=(15, 23, 42), direction="ltr")
    _draw_text(draw, (price_x - 20, 215), "تومان", f_unit, (100, 116, 139))

    # Percentage Pill
    sign = "+" if change_pct >= 0 else ""
    pct_text = f"{sign}{change_pct:.2f}%"
    badge_color = (220, 252, 231) if change_pct >= 0 else (254, 226, 226)
    text_color = (22, 101, 52) if change_pct >= 0 else (153, 27, 27)
    arrow = "↑" if change_pct >= 0 else "↓"

    bbox_pct = draw.textbbox((0,0), f"{arrow} {pct_text}", font=f_small, direction="ltr")
    pill_w = (bbox_pct[2] - bbox_pct[0]) + 40
    
    badge_x1 = card_x1 - 60
    badge_x0 = badge_x1 - pill_w
    badge_y0, badge_y1 = 320, 375
    
    draw.rounded_rectangle((badge_x0, badge_y0, badge_x1, badge_y1), radius=25, fill=badge_color)
    draw.text((badge_x0 + 20, badge_y0 + 8), f"{arrow} {pct_text}", font=f_small, fill=text_color, direction="ltr")

    # Chart
    chart_box = (card_x0 + 120, 430, card_x1 - 60, H - 140)
    line_color = (34, 197, 94) if change_pct >= 0 else (239, 68, 68)
    fill_color = (34, 197, 94, 50) if change_pct >= 0 else (239, 68, 68, 50)
    draw_area_chart(draw, values, chart_box, line_color, fill_color, f_tiny)

    # Footer
    _draw_text(draw, (W // 2, H - 80), "@CoinVEX | @Vibe", f_tiny, (120, 120, 120), direction="ltr", align="center")
    _draw_text(draw, (card_x1 - 60, H - 140), f"بروزرسانی: {age_text}", f_tiny, (120, 120, 120))
    
    out = BytesIO()
    out.name = "price-card.png"
    img.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out
