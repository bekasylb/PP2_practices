import pygame


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, font):
        pygame.draw.rect(screen, (220, 220, 220), self.rect, border_radius=10)
        pygame.draw.rect(screen, (40, 40, 40), self.rect, 2, border_radius=10)
        text_surface = font.render(self.text, True, (20, 20, 20))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mx, my):
        return self.rect.collidepoint(mx, my)


def draw_text(screen, text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_centered_text(screen, text, font, color, center_x, center_y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(center_x, center_y))
    screen.blit(surface, rect)


def get_username_input(screen, clock, width, height):
    font = pygame.font.SysFont("Arial", 30)
    title_font = pygame.font.SysFont("Arial", 40, bold=True)
    name = ""

    running = True
    while running:
        screen.fill((20, 20, 30))
        draw_centered_text(screen, "Enter Username", title_font, (255, 255, 255), width // 2, 170)
        pygame.draw.rect(screen, (255, 255, 255), (100, 280, 300, 50), border_radius=8)
        pygame.draw.rect(screen, (30, 30, 30), (100, 280, 300, 50), 2, border_radius=8)

        shown = name + "|"
        draw_text(screen, shown, font, (20, 20, 20), 115, 292)
        draw_centered_text(screen, "Enter = start, Esc = cancel", font, (220, 220, 220), width // 2, 400)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cleaned = name.strip()
                    if cleaned:
                        return cleaned
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if event.unicode.isprintable() and len(name) < 12:
                        name += event.unicode

        pygame.display.flip()
        clock.tick(60)