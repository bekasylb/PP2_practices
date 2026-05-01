import pygame
from datetime import datetime
from tools import (
    draw_smooth_line,
    draw_rectangle,
    draw_square,
    draw_circle,
    draw_right_triangle,
    draw_equilateral_triangle,
    draw_rhombus,
    flood_fill,
)

pygame.init()

WIDTH = 1200
HEIGHT = 750
TOOLBAR_HEIGHT = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20)
text_font = pygame.font.SysFont("Arial", 28)

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

mode = "pencil"
color = (0, 0, 0)
brush_size = 5

drawing = False
start_pos = None
current_pos = None
last_pos = None

text_mode_active = False
text_position = None
text_buffer = ""


def draw_text(text, x, y, text_color=(0, 0, 0)):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def save_canvas():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{timestamp}.png"
    save_surface = canvas.subsurface((0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)).copy()
    pygame.image.save(save_surface, filename)
    print(f"Saved: {filename}")


def draw_toolbar():
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, (180, 180, 180), (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    for button in buttons:
        pygame.draw.rect(screen, button["bg"], button["rect"], border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), button["rect"], 2, border_radius=8)

        text_surface = font.render(button["label"], True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button["rect"].center)
        screen.blit(text_surface, text_rect)

    draw_text(f"Mode: {mode}", 930, 12)
    draw_text(f"Brush: {brush_size}px", 930, 42)
    draw_text("Sizes: 1=2px  2=5px  3=10px", 930, 72)

    pygame.draw.rect(screen, color, (1110, 22, 45, 45))
    pygame.draw.rect(screen, (0, 0, 0), (1110, 22, 45, 45), 2)


def apply_shape(surface, active_mode, p1, p2, draw_color, width):
    if active_mode == "line":
        pygame.draw.line(surface, draw_color, p1, p2, width)
    elif active_mode == "rectangle":
        draw_rectangle(surface, p1, p2, draw_color, width)
    elif active_mode == "circle":
        draw_circle(surface, p1, p2, draw_color, width)
    elif active_mode == "square":
        draw_square(surface, p1, p2, draw_color, width)
    elif active_mode == "right_triangle":
        draw_right_triangle(surface, p1, p2, draw_color, width)
    elif active_mode == "equilateral_triangle":
        draw_equilateral_triangle(surface, p1, p2, draw_color, width)
    elif active_mode == "rhombus":
        draw_rhombus(surface, p1, p2, draw_color, width)


buttons = [
    {"label": "Pencil", "rect": pygame.Rect(10, 15, 90, 40), "action": "pencil", "bg": (245, 245, 245)},
    {"label": "Line", "rect": pygame.Rect(110, 15, 80, 40), "action": "line", "bg": (245, 245, 245)},
    {"label": "Rect", "rect": pygame.Rect(200, 15, 75, 40), "action": "rectangle", "bg": (245, 245, 245)},
    {"label": "Circle", "rect": pygame.Rect(285, 15, 80, 40), "action": "circle", "bg": (245, 245, 245)},
    {"label": "Eraser", "rect": pygame.Rect(375, 15, 85, 40), "action": "eraser", "bg": (245, 245, 245)},
    {"label": "Fill", "rect": pygame.Rect(470, 15, 70, 40), "action": "fill", "bg": (245, 245, 245)},
    {"label": "Text", "rect": pygame.Rect(550, 15, 70, 40), "action": "text", "bg": (245, 245, 245)},

    {"label": "Square", "rect": pygame.Rect(10, 65, 90, 40), "action": "square", "bg": (245, 245, 245)},
    {"label": "R-Tri", "rect": pygame.Rect(110, 65, 80, 40), "action": "right_triangle", "bg": (245, 245, 245)},
    {"label": "E-Tri", "rect": pygame.Rect(200, 65, 80, 40), "action": "equilateral_triangle", "bg": (245, 245, 245)},
    {"label": "Rhomb", "rect": pygame.Rect(290, 65, 90, 40), "action": "rhombus", "bg": (245, 245, 245)},
    {"label": "Clear", "rect": pygame.Rect(390, 65, 80, 40), "action": "clear", "bg": (255, 220, 220)},

    {"label": "Red", "rect": pygame.Rect(490, 65, 70, 40), "action": (255, 0, 0), "bg": (255, 150, 150)},
    {"label": "Green", "rect": pygame.Rect(570, 65, 80, 40), "action": (0, 180, 0), "bg": (150, 255, 150)},
    {"label": "Blue", "rect": pygame.Rect(660, 65, 75, 40), "action": (0, 0, 255), "bg": (150, 150, 255)},
    {"label": "Black", "rect": pygame.Rect(745, 65, 80, 40), "action": (0, 0, 0), "bg": (220, 220, 220)},
]


running = True
while running:
    screen.blit(canvas, (0, 0))
    draw_toolbar()

    if drawing and mode in (
        "line",
        "rectangle",
        "circle",
        "square",
        "right_triangle",
        "equilateral_triangle",
        "rhombus",
    ) and start_pos and current_pos:
        apply_shape(screen, mode, start_pos, current_pos, color, brush_size)

    if text_mode_active and text_position:
        preview = text_font.render(text_buffer + "|", True, color)
        screen.blit(preview, text_position)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            ctrl_held = pygame.key.get_mods() & pygame.KMOD_CTRL

            # Save canvas
            if ctrl_held and event.key == pygame.K_s:
                save_canvas()

            elif text_mode_active:
                if event.key == pygame.K_RETURN:
                    if text_buffer:
                        text_surface = text_font.render(text_buffer, True, color)
                        canvas.blit(text_surface, text_position)
                    text_mode_active = False
                    text_position = None
                    text_buffer = ""

                elif event.key == pygame.K_ESCAPE:
                    text_mode_active = False
                    text_position = None
                    text_buffer = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]

                else:
                    if event.unicode.isprintable():
                        text_buffer += event.unicode

            else:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False

                # Brush sizes
                elif event.key == pygame.K_1:
                    brush_size = 2
                elif event.key == pygame.K_2:
                    brush_size = 5
                elif event.key == pygame.K_3:
                    brush_size = 10

                # Colors
                elif event.key == pygame.K_r:
                    color = (255, 0, 0)
                elif event.key == pygame.K_g:
                    color = (0, 180, 0)
                elif event.key == pygame.K_b:
                    color = (0, 0, 255)
                elif event.key == pygame.K_k:
                    color = (0, 0, 0)

                # Clear
                elif event.key == pygame.K_c:
                    pygame.draw.rect(canvas, (255, 255, 255), (0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT))

                # Tool shortcuts
                elif event.key == pygame.K_p:
                    mode = "pencil"
                elif event.key == pygame.K_l:
                    mode = "line"
                elif event.key == pygame.K_e:
                    mode = "eraser"
                elif event.key == pygame.K_f:
                    mode = "fill"
                elif event.key == pygame.K_t:
                    mode = "text"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Toolbar buttons
            if my <= TOOLBAR_HEIGHT:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        action = button["action"]

                        if action in (
                            "pencil",
                            "line",
                            "rectangle",
                            "circle",
                            "eraser",
                            "fill",
                            "text",
                            "square",
                            "right_triangle",
                            "equilateral_triangle",
                            "rhombus",
                        ):
                            mode = action
                        elif action == "clear":
                            pygame.draw.rect(
                                canvas,
                                (255, 255, 255),
                                (0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT),
                            )
                        elif isinstance(action, tuple):
                            color = action
                continue

            if mode == "fill":
                flood_fill(canvas, event.pos, color, TOOLBAR_HEIGHT)
                continue

            if mode == "text":
                text_mode_active = True
                text_position = event.pos
                text_buffer = ""
                continue

            if event.button == 1:
                drawing = True
                start_pos = event.pos
                current_pos = event.pos
                last_pos = event.pos

                if mode == "pencil":
                    pygame.draw.circle(canvas, color, event.pos, brush_size)
                elif mode == "eraser":
                    pygame.draw.circle(canvas, (255, 255, 255), event.pos, brush_size)

        elif event.type == pygame.MOUSEMOTION:
            current_pos = event.pos

            if drawing and event.pos[1] > TOOLBAR_HEIGHT:
                if mode == "pencil":
                    draw_smooth_line(canvas, last_pos, event.pos, brush_size, color)
                    last_pos = event.pos
                elif mode == "eraser":
                    draw_smooth_line(canvas, last_pos, event.pos, brush_size, (255, 255, 255))
                    last_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                end_pos = event.pos

                if end_pos[1] > TOOLBAR_HEIGHT and mode in (
                    "line",
                    "rectangle",
                    "circle",
                    "square",
                    "right_triangle",
                    "equilateral_triangle",
                    "rhombus",
                ):
                    apply_shape(canvas, mode, start_pos, end_pos, color, brush_size)

                start_pos = None
                current_pos = None
                last_pos = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
