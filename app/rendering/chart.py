from PIL import ImageDraw


def draw_line_chart(
    draw: ImageDraw.ImageDraw,
    values: list[float],
    box: tuple[int, int, int, int],
    color: tuple[int, int, int] = (45, 210, 130),
    width: int = 5,
) -> None:
    if len(values) < 2:
        return
    left, top, right, bottom = box
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    span = right - left
    points = []
    for i, v in enumerate(values):
        x = left + i * span / (len(values) - 1)
        y = bottom - (v - lo) / (hi - lo) * (bottom - top)
        points.append((int(x), int(y)))
    draw.line(points, fill=color, width=width, joint="curve")
    ex, ey = points[-1]
    r = 6
    draw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=color)
