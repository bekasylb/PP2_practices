import pygame

pygame.init()

WIDTH = 1000
HEIGHT = 700
TOOLBAR_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))


mode = "brush"
color = (0, 0, 255)
brush_size = 6
eraser_size = 20

drawing = False
last_pos = None
start_pos = None
current_pos = None


def draw_text(text, x, y, color=(0, 0, 0)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_line(surface, start, end, width, color):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy), 1)

    for i in range(iterations):
        progress = i / iterations
        x = int(start[0] + (end[0] - start[0]) * progress)
        y = int(start[1] + (end[1] - start[1]) * progress)
        pygame.draw.circle(surface, color, (x, y), width)


def draw_toolbar():
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, (180, 180, 180), (0, TOOLBAR_HEIGHT), (WIDTH, TOOLBAR_HEIGHT), 2)

    for button in buttons:
        pygame.draw.rect(screen, button["color"], button["rect"], border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), button["rect"], 2, border_radius=8)
        draw_text(button["label"], button["rect"].x + 8, button["rect"].y + 10)

    draw_text(f"Mode: {mode}", 720, 10)
    draw_text(f"Size: {brush_size}", 720, 35)

    pygame.draw.rect(screen, color, (900, 15, 40, 40))
    pygame.draw.rect(screen, (0, 0, 0), (900, 15, 40, 40), 2)


buttons = [
    {"label": "Brush", "rect": pygame.Rect(10, 15, 90, 40), "action": "brush", "color": (245, 245, 245)},
    {"label": "Rect", "rect": pygame.Rect(110, 15, 90, 40), "action": "rectangle", "color": (245, 245, 245)},
    {"label": "Circle", "rect": pygame.Rect(210, 15, 90, 40), "action": "circle", "color": (245, 245, 245)},
    {"label": "Eraser", "rect": pygame.Rect(310, 15, 90, 40), "action": "eraser", "color": (245, 245, 245)},
    {"label": "Clear", "rect": pygame.Rect(410, 15, 90, 40), "action": "clear", "color": (255, 230, 230)},

    {"label": "Red", "rect": pygame.Rect(520, 15, 70, 40), "action": (255, 0, 0), "color": (255, 150, 150)},
    {"label": "Green", "rect": pygame.Rect(600, 15, 80, 40), "action": (0, 180, 0), "color": (150, 255, 150)},
    {"label": "Blue", "rect": pygame.Rect(690, 15, 80, 40), "action": (0, 0, 255), "color": (150, 150, 255)},
]


running = True
while running:
    screen.blit(canvas, (0, 0))
    draw_toolbar()

    if drawing and mode in ("rectangle", "circle") and start_pos and current_pos:
        if mode == "rectangle":
            x1, y1 = start_pos
            x2, y2 = current_pos
            rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            pygame.draw.rect(screen, color, rect, 2)
        elif mode == "circle":
            radius = int(((current_pos[0] - start_pos[0]) ** 2 + (current_pos[1] - start_pos[1]) ** 2) ** 0.5)
            pygame.draw.circle(screen, color, start_pos, radius, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                color = (255, 0, 0)
            elif event.key == pygame.K_g:
                color = (0, 180, 0)
            elif event.key == pygame.K_b:
                color = (0, 0, 255)
            elif event.key == pygame.K_k:
                color = (0, 0, 0)
            elif event.key == pygame.K_1:
                mode = "brush"
            elif event.key == pygame.K_2:
                mode = "rectangle"
            elif event.key == pygame.K_3:
                mode = "circle"
            elif event.key == pygame.K_4:
                mode = "eraser"
            elif event.key == pygame.K_c:
                canvas.fill((255, 255, 255))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if my <= TOOLBAR_HEIGHT:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        action = button["action"]
                        if action in ("brush", "rectangle", "circle", "eraser"):
                            mode = action
                        elif action == "clear":
                            canvas.fill((255, 255, 255))
                        elif isinstance(action, tuple):
                            color = action
                continue

            if event.button == 1:
                drawing = True
                start_pos = event.pos
                current_pos = event.pos
                last_pos = event.pos

                if mode == "brush":
                    pygame.draw.circle(canvas, color, event.pos, brush_size)
                elif mode == "eraser":
                    pygame.draw.circle(canvas, (255, 255, 255), event.pos, eraser_size)

            elif event.button == 4:
                brush_size = min(50, brush_size + 1)
            elif event.button == 5:
                brush_size = max(1, brush_size - 1)

        elif event.type == pygame.MOUSEMOTION:
            current_pos = event.pos

            if drawing and event.pos[1] > TOOLBAR_HEIGHT:
                if mode == "brush":
                    draw_line(canvas, last_pos, event.pos, brush_size, color)
                    last_pos = event.pos
                elif mode == "eraser":
                    draw_line(canvas, last_pos, event.pos, eraser_size, (255, 255, 255))
                    last_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False
                end_pos = event.pos

                if mode == "rectangle" and start_pos and end_pos[1] > TOOLBAR_HEIGHT:
                    x1, y1 = start_pos
                    x2, y2 = end_pos
                    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                    pygame.draw.rect(canvas, color, rect, 2)

                elif mode == "circle" and start_pos and end_pos[1] > TOOLBAR_HEIGHT:
                    radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                    pygame.draw.circle(canvas, color, start_pos, radius, 2)

                start_pos = None
                current_pos = None
                last_pos = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
