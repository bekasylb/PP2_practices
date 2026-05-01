import pygame
from collections import deque


def get_rect_from_points(p1, p2):
    """Create a pygame.Rect from two corner points."""
    x1, y1 = p1
    x2, y2 = p2
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def draw_smooth_line(surface, start, end, width, color):
    """Draw a smooth line using circles between two points."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(abs(dx), abs(dy), 1)

    for i in range(steps + 1):
        t = i / steps
        x = int(start[0] + dx * t)
        y = int(start[1] + dy * t)
        pygame.draw.circle(surface, color, (x, y), width)


def draw_rectangle(surface, p1, p2, color, width):
    rect = get_rect_from_points(p1, p2)
    pygame.draw.rect(surface, color, rect, width)


def draw_square(surface, p1, p2, color, width):
    x1, y1 = p1
    x2, y2 = p2

    side = min(abs(x2 - x1), abs(y2 - y1))

    rect_x = x1 - side if x2 < x1 else x1
    rect_y = y1 - side if y2 < y1 else y1

    rect = pygame.Rect(rect_x, rect_y, side, side)
    pygame.draw.rect(surface, color, rect, width)


def draw_circle(surface, p1, p2, color, width):
    radius = int(((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5)
    pygame.draw.circle(surface, color, p1, radius, width)


def draw_right_triangle(surface, p1, p2, color, width):
    x1, y1 = p1
    x2, y2 = p2
    points = [(x1, y2), (x1, y1), (x2, y2)]
    pygame.draw.polygon(surface, color, points, width)


def draw_equilateral_triangle(surface, p1, p2, color, width):
    x1, y1 = p1
    x2, y2 = p2

    side = abs(x2 - x1)
    if side == 0:
        return

    height = int((3 ** 0.5 / 2) * side)

    top_x = x1 + (x2 - x1) // 2
    top_y = y1

    if x2 >= x1:
        left = (x1, y1 + height)
        right = (x1 + side, y1 + height)
    else:
        left = (x1 - side, y1 + height)
        right = (x1, y1 + height)

    points = [(top_x, top_y), left, right]
    pygame.draw.polygon(surface, color, points, width)


def draw_rhombus(surface, p1, p2, color, width):
    rect = get_rect_from_points(p1, p2)

    cx = rect.x + rect.width // 2
    cy = rect.y + rect.height // 2

    top = (cx, rect.y)
    right = (rect.x + rect.width, cy)
    bottom = (cx, rect.y + rect.height)
    left = (rect.x, cy)

    pygame.draw.polygon(surface, color, [top, right, bottom, left], width)


def flood_fill(surface, start_pos, fill_color, bounds_top):
    """
    Flood fill using get_at / set_at.
    Stops at pixels of a different exact color.
    Does not fill inside toolbar area.
    """
    width, height = surface.get_size()
    x, y = start_pos

    if x < 0 or y < bounds_top or x >= width or y >= height:
        return

    target_color = surface.get_at((x, y))
    fill_color_rgba = pygame.Color(*fill_color)

    if target_color == fill_color_rgba:
        return

    q = deque()
    q.append((x, y))

    while q:
        cx, cy = q.popleft()

        if cx < 0 or cy < bounds_top or cx >= width or cy >= height:
            continue

        if surface.get_at((cx, cy)) != target_color:
            continue

        surface.set_at((cx, cy), fill_color_rgba)

        q.append((cx + 1, cy))
        q.append((cx - 1, cy))
        q.append((cx, cy + 1))
        q.append((cx, cy - 1))