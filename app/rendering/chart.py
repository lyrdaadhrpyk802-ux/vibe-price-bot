from PIL import Image, ImageDraw

def draw_area_chart(draw, values, box, color, fill_color):
    if len(values) < 2:
        return

    left, top, right, bottom = box
    min_value, max_value = min(values), max(values)
    if max_value == min_value:
        max_value += 1

    points = []
    for index, value in enumerate(values):
        x = left + index * (right - left) / (len(values) - 1)
        normalized = (value - min_value) / (max_value - min_value)
        y = bottom - normalized * (bottom - top)
        points.append((int(x), int(y)))

    polygon_points = [(left, bottom)] + points + [(right, bottom)]
    draw.polygon(polygon_points, fill=fill_color)
    draw.line(points, fill=color, width=4, joint="curve")

    x, y = points[-1]
    draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=color)
