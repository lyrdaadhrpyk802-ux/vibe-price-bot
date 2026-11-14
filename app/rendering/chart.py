from PIL import ImageDraw

def draw_area_chart(draw, values, box, color, fill_color, font):
    if len(values) < 2:
        return

    left, top, right, bottom = box
    min_value, max_value = min(values), max(values)
    if max_value == min_value:
        max_value += 1

    # Draw grid lines and Y-axis labels
    steps = 4
    for i in range(steps + 1):
        y = bottom - i * (bottom - top) / steps
        val = min_value + i * (max_value - min_value) / steps
        
        # Draw line
        draw.line([(left, y), (right, y)], fill=(230, 230, 230), width=1)
        
        # Draw label (LTR)
        val_text = f"{int(val):,}"
        bbox = draw.textbbox((0, 0), val_text, font=font, direction="ltr")
        w = bbox[2] - bbox[0]
        draw.text((left - w - 15, y - 12), val_text, font=font, fill=(150, 150, 150), direction="ltr")

    points = []
    for index, value in enumerate(values):
        x = left + index * (right - left) / (len(values) - 1)
        normalized = (value - min_value) / (max_value - min_value)
        y = bottom - normalized * (bottom - top)
        points.append((int(x), int(y)))

    # Draw filled area
    polygon_points = [(left, bottom)] + points + [(right, bottom)]
    draw.polygon(polygon_points, fill=fill_color)

    # Draw line
    draw.line(points, fill=color, width=4, joint="curve")

    # Draw last point dot
    x, y = points[-1]
    draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=color)
