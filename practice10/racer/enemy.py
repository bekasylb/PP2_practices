import pygame
import random


class Enemy:
    def __init__(self, screen_width):
        self.width = 50
        self.height = 90
        self.screen_width = screen_width

        #Spawn enemy at random x position at the top
        self.rect = pygame.Rect(
            random.randint(20, self.screen_width - self.width - 20),
            random.randint(-300, -100),
            self.width,
            self.height
        )
        self.color = (220, 50, 50)

    def update(self, speed):
        self.rect.y += speed

        return self.rect.top > 600

    def reset(self):
        self.rect.x = random.randint(20, self.screen_width - self.width - 20)
        self.rect.y = random.randint(-300, -100)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)

        window_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, 20)
        pygame.draw.rect(screen, (255, 220, 220), window_rect, border_radius=5)

        pygame.draw.rect(screen, (30, 30, 30), (self.rect.x - 4, self.rect.y + 8, 8, 16), border_radius=3)
        pygame.draw.rect(screen, (30, 30, 30), (self.rect.right - 4, self.rect.y + 8, 8, 16), border_radius=3)
        pygame.draw.rect(screen, (30, 30, 30), (self.rect.x - 4, self.rect.bottom - 24, 8, 16), border_radius=3)
        pygame.draw.rect(screen, (30, 30, 30), (self.rect.right - 4, self.rect.bottom - 24, 8, 16), border_radius=3)
