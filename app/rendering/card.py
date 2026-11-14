from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = Path(__file__).resolve().parent.parent.parent / "fonts"
FONT_REGULAR = FONT_DIR / "Vazirmatn-Regular.ttf"
FONT_BOLD = FONT_DIR / "Vazirmatn-Bold.ttf"

def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.load_default() if not path.exists() else ImageFont.truetype(str(path), size)
    return ImageFont.load_default()

def _draw_text(draw, xy, text, font, fill, align="right", direction="rtl"):
    try:
        bbox = draw.textbbox((0, 0), text, font=font, direction=direction, language="fa" if direction=="rtl" else "en")
        w = bbox[2] - bbox[0]
        x = xy[0] - w if align == "right" else xy[0]
        draw.text((x, xy[1]), text, font=font, fill=fill, direction=direction, language="fa" if direction=="rtl" else "en")
    except Exception:
        # Fallback if libraqm is missing
        draw.text(xy, text, font=font, fill=fill)

def make_price_card(title, price_text, unit, change_pct, values, age_text, source, is_stale):
    W, H = 1200, 700
    
    # Asset specific colors (Background, Line, Fill)
    colors = {
        "دلار آمریکا": ((30, 58, 138), (34, 197, 94), (34, 197, 94, 80)),
        "طلا ۱۸ عیار": ((113, 63, 18), (250, 204, 21), (250, 204, 21, 80)),
        "بیت کوین": ((124, 45, 18), (249, 115, 22), (249, 115, 22, 80)),
        "یورو": ((15, 118, 110), (16, 185, 129), (16, 185, 129, 80)),
        "default": ((30, 41, 59), (56, 189, 248), (56, 189, 248, 80))
    }
    bg_color, line_color, fill_color = colors.get(title, colors["default"])
    
    if change_pct < 0:
        line_color = (239, 68, 68) # Red
        fill_color = (239, 68, 68, 80)

    # 1. Base Background with Blur
    bg = Image.new("RGB", (W, H), bg_color)
    draw_bg = ImageDraw.Draw(bg)
    # Draw some random huge circles for a mesh gradient look
    draw_bg.ellipse((W//4, -200, W, H//2), fill=(255, 255, 255, 30))
    draw_bg.ellipse((-200, H//2, W//2, H), fill=(0, 0, 0, 50))
    bg = bg.filter(ImageFilter.GaussianBlur(100))
    
    # 2. Main Card (White)
    img = Image.new("RGBA", (W, H))
    img.paste(bg, (0, 0))
    draw = ImageDraw.Draw(img)
    
    card_x0, card_y0, card_x1, card_y1 = 60, 60, W - 60, H - 60
    draw.rounded_rectangle((card_x0, card_y0, card_x1, card_y1), radius=40, fill=(255, 255, 255, 255))

    # Fonts
    f_title = _font(FONT_BOLD, 42)
    f_price = _font(FONT_BOLD, 85)
    f_small = _font(FONT_REGULAR, 28)
    f_tiny  = _font(FONT_REGULAR, 22)

    # 3. Draw Text (RTL)
    _draw_text(draw, (card_x1 - 60, 120), title, f_title, (30, 41, 59))
    _draw_text(draw, (card_x1 - 60, 200), price_text, f_price, (15, 23, 42))
    _draw_text(draw, (card_x1 - 60, 310), unit, f_small, (100, 116, 139))

    # 4. Percentage Badge
    sign = "+" if change_pct >= 0 else ""
    pct_text = f"{sign}{change_pct:.2f}%"
    badge_color = (220, 252, 231) if change_pct >= 0 else (254, 226, 226) # Light green/red
    text_color = (22, 101, 52) if change_pct >= 0 else (153, 27, 27) # Dark green/red
    arrow = "▲" if change_pct >= 0 else "▼"

    # Draw a rounded rectangle for badge
    badge_x0, badge_y0 = card_x1 - 200, 380
    badge_x1, badge_y1 = card_x1 - 60, 435
    draw.rounded_rectangle((badge_x0, badge_y0, badge_x1, badge_y1), radius=20, fill=badge_color)
    
    # Draw pct text LTR inside badge
    _draw_text(draw, (badge_x0 + 20, badge_y0 + 5), f"{arrow} {pct_text}", f_small, text_color, direction="ltr", align="left")

    # 5. Draw Chart (Bottom Left)
    chart_box = (120, 480, W - 120, H - 100)
    draw_area_chart(draw, values, chart_box, line_color, fill_color)

    # 6. Footer text
    _draw_text(draw, (W - 120, H - 90), f"بروزرسانی: {age_text}", f_tiny, (100, 116, 139))
    _draw_text(draw, (120, H - 90), f"منبع: {source.upper()}", f_tiny, (100, 116, 139), direction="ltr", align="left")

    out = BytesIO()
    out.name = "price-card.png"
    img.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out
