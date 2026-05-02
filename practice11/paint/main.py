import pygame

import math


pygame.init()


WIDTH = 1000
HEIGHT = 700
TOOLBAR_HEIGHT = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice11 Paint")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

mode = "brush"
color = (0, 0, 0)
brush_size = 5
eraser_size = 20

drawing = False
start_pos = None
current_pos = None
last_pos = None


def draw_text(text, x, y, text_color=(0, 0, 0)):
    """Draw text on the main screen."""
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def draw_smooth_line(surface, start, end, width, draw_color):
    """Draw a smooth line between two mouse points using circles."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(abs(dx), abs(dy), 1)

    for i in range(steps + 1):
        progress = i / steps
        x = int(start[0] + dx * progress)
        y = int(start[1] + dy * progress)
        pygame.draw.circle(surface, draw_color, (x, y), width)


def get_rect_from_points(p1, p2):
    """Create a rectangle using two corner points."""
    x1, y1 = p1
    x2, y2 = p2
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def draw_toolbar():
    """Draw top toolbar with buttons and current settings."""
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, (180, 180, 180), (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    for button in buttons:
        pygame.draw.rect(screen, button["bg"], button["rect"], border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), button["rect"], 2, border_radius=8)

        text_surface = font.render(button["label"], True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button["rect"].center)
        screen.blit(text_surface, text_rect)

    draw_text(f"Mode: {mode}", 770, 15)
    draw_text(f"Size: {brush_size}", 770, 50)

    pygame.draw.rect(screen, color, (920, 25, 40, 40))
    pygame.draw.rect(screen, (0, 0, 0), (920, 25, 40, 40), 2)


def draw_right_triangle(surface, p1, p2, draw_color, width=2):
    """Draw a right triangle inside the rectangle created by p1 and p2."""
    x1, y1 = p1
    x2, y2 = p2
    points = [(x1, y2), (x1, y1), (x2, y2)]
    pygame.draw.polygon(surface, draw_color, points, width)


def draw_equilateral_triangle(surface, p1, p2, draw_color, width=2):
    """Draw an equilateral-style triangle using the drag width."""
    x1, y1 = p1
    x2, y2 = p2

    side = abs(x2 - x1)
    if side == 0:
        return

    height = int((math.sqrt(3) / 2) * side)

    top_x = x1 + (x2 - x1) // 2
    top_y = y1
    left_x = x1
    left_y = y1 + height
    right_x = x1 + side
    right_y = y1 + height

    # If dragged left, mirror the figure
    if x2 < x1:
        left_x = x1 - side
        right_x = x1

    points = [(top_x, top_y), (left_x, left_y), (right_x, right_y)]
    pygame.draw.polygon(surface, draw_color, points, width)


def draw_rhombus(surface, p1, p2, draw_color, width=2):
    """Draw a rhombus inside the rectangle created by p1 and p2."""
    rect = get_rect_from_points(p1, p2)

    cx = rect.x + rect.width // 2
    cy = rect.y + rect.height // 2

    top = (cx, rect.y)
    right = (rect.x + rect.width, cy)
    bottom = (cx, rect.y + rect.height)
    left = (rect.x, cy)

    pygame.draw.polygon(surface, draw_color, [top, right, bottom, left], width)


def draw_square(surface, p1, p2, draw_color, width=2):
    """Draw a square using the smaller side from mouse drag."""
    x1, y1 = p1
    x2, y2 = p2

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 < x1:
        rect_x = x1 - side
    else:
        rect_x = x1

    if y2 < y1:
        rect_y = y1 - side
    else:
        rect_y = y1

    rect = pygame.Rect(rect_x, rect_y, side, side)
    pygame.draw.rect(surface, draw_color, rect, width)


# Toolbar buttons
buttons = [
    {"label": "Brush", "rect": pygame.Rect(10, 15, 80, 45), "action": "brush", "bg": (245, 245, 245)},
    {"label": "Rect", "rect": pygame.Rect(100, 15, 75, 45), "action": "rectangle", "bg": (245, 245, 245)},
    {"label": "Circle", "rect": pygame.Rect(185, 15, 80, 45), "action": "circle", "bg": (245, 245, 245)},
    {"label": "Eraser", "rect": pygame.Rect(275, 15, 85, 45), "action": "eraser", "bg": (245, 245, 245)},
    {"label": "Square", "rect": pygame.Rect(370, 15, 85, 45), "action": "square", "bg": (245, 245, 245)},
    {"label": "R-Tri", "rect": pygame.Rect(465, 15, 75, 45), "action": "right_triangle", "bg": (245, 245, 245)},
    {"label": "E-Tri", "rect": pygame.Rect(550, 15, 75, 45), "action": "equilateral_triangle", "bg": (245, 245, 245)},
    {"label": "Rhomb", "rect": pygame.Rect(635, 15, 85, 45), "action": "rhombus", "bg": (245, 245, 245)},

    {"label": "Clear", "rect": pygame.Rect(10, 70, 80, 35), "action": "clear", "bg": (255, 220, 220)},
    {"label": "Red", "rect": pygame.Rect(100, 70, 70, 35), "action": (255, 0, 0), "bg": (255, 150, 150)},
    {"label": "Green", "rect": pygame.Rect(180, 70, 85, 35), "action": (0, 180, 0), "bg": (150, 255, 150)},
    {"label": "Blue", "rect": pygame.Rect(275, 70, 75, 35), "action": (0, 0, 255), "bg": (150, 150, 255)},
    {"label": "Black", "rect": pygame.Rect(360, 70, 80, 35), "action": (0, 0, 0), "bg": (220, 220, 220)},
]

# Main loop
running = True
while running:
    screen.blit(canvas, (0, 0))
    draw_toolbar()

    # Show preview for shape modes while dragging
    if drawing and mode in (
        "rectangle",
        "circle",
        "square",
        "right_triangle",
        "equilateral_triangle",
        "rhombus",
    ) and start_pos and current_pos:
        if mode == "rectangle":
            rect = get_rect_from_points(start_pos, current_pos)
            pygame.draw.rect(screen, color, rect, 2)

        elif mode == "circle":
            radius = int(((current_pos[0] - start_pos[0]) ** 2 + (current_pos[1] - start_pos[1]) ** 2) ** 0.5)
            pygame.draw.circle(screen, color, start_pos, radius, 2)

        elif mode == "square":
            draw_square(screen, start_pos, current_pos, color, 2)

        elif mode == "right_triangle":
            draw_right_triangle(screen, start_pos, current_pos, color, 2)

        elif mode == "equilateral_triangle":
            draw_equilateral_triangle(screen, start_pos, current_pos, color, 2)

        elif mode == "rhombus":
            draw_rhombus(screen, start_pos, current_pos, color, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Exit
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False

            # Modes
            elif event.key == pygame.K_1:
                mode = "brush"
            elif event.key == pygame.K_2:
                mode = "rectangle"
            elif event.key == pygame.K_3:
                mode = "circle"
            elif event.key == pygame.K_4:
                mode = "eraser"
            elif event.key == pygame.K_5:
                mode = "square"
            elif event.key == pygame.K_6:
                mode = "right_triangle"
            elif event.key == pygame.K_7:
                mode = "equilateral_triangle"
            elif event.key == pygame.K_8:
                mode = "rhombus"

            # Colors
            elif event.key == pygame.K_r:
                color = (255, 0, 0)
            elif event.key == pygame.K_g:
                color = (0, 180, 0)
            elif event.key == pygame.K_b:
                color = (0, 0, 255)
            elif event.key == pygame.K_k:
                color = (0, 0, 0)

            # Clear canvas
            elif event.key == pygame.K_c:
                canvas.fill((255, 255, 255))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Click on toolbar buttons
            if my <= TOOLBAR_HEIGHT:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        action = button["action"]

                        if action in (
                            "brush",
                            "rectangle",
                            "circle",
                            "eraser",
                            "square",
                            "right_triangle",
                            "equilateral_triangle",
                            "rhombus",
                        ):
                            mode = action
                        elif action == "clear":
                            canvas.fill((255, 255, 255))
                        elif isinstance(action, tuple):
                            color = action
                continue

            # Left click starts drawing
            if event.button == 1:
                drawing = True
                start_pos = event.pos
                current_pos = event.pos
                last_pos = event.pos

                if mode == "brush":
                    pygame.draw.circle(canvas, color, event.pos, brush_size)
                elif mode == "eraser":
                    pygame.draw.circle(canvas, (255, 255, 255), event.pos, eraser_size)

            # Mouse wheel up increases brush size
            elif event.button == 4:
                brush_size = min(50, brush_size + 1)

            # Mouse wheel down decreases brush size
            elif event.button == 5:
                brush_size = max(1, brush_size - 1)

        elif event.type == pygame.MOUSEMOTION:
            current_pos = event.pos

            if drawing and event.pos[1] > TOOLBAR_HEIGHT:
                if mode == "brush":
                    draw_smooth_line(canvas, last_pos, event.pos, brush_size, color)
                    last_pos = event.pos
                elif mode == "eraser":
                    draw_smooth_line(canvas, last_pos, event.pos, eraser_size, (255, 255, 255))
                    last_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                end_pos = event.pos

                if end_pos[1] > TOOLBAR_HEIGHT:
                    if mode == "rectangle":
                        rect = get_rect_from_points(start_pos, end_pos)
                        pygame.draw.rect(canvas, color, rect, 2)

                    elif mode == "circle":
                        radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                        pygame.draw.circle(canvas, color, start_pos, radius, 2)

                    elif mode == "square":
                        draw_square(canvas, start_pos, end_pos, color, 2)

                    elif mode == "right_triangle":
                        draw_right_triangle(canvas, start_pos, end_pos, color, 2)

                    elif mode == "equilateral_triangle":
                        draw_equilateral_triangle(canvas, start_pos, end_pos, color, 2)

                    elif mode == "rhombus":
                        draw_rhombus(canvas, start_pos, end_pos, color, 2)

                start_pos = None
                current_pos = None
                last_pos = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
