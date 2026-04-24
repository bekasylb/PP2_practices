import pygame
import random


class Coin:
    def __init__(self, screen_width):
        self.radius = 12
        self.screen_width = screen_width
        self.color = (255, 215, 0)

        self.x = random.randint(20 + self.radius, self.screen_width - 20 - self.radius)
        self.y = random.randint(-500, -100)
        self.speed = 5

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self):
        self.y += self.speed
        return self.y - self.radius > 600

    def reset(self):
        self.x = random.randint(20 + self.radius, self.screen_width - 20 - self.radius)
        self.y = random.randint(-500, -100)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 235, 120), (self.x, self.y), self.radius - 4)
