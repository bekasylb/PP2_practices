import pygame
import random


class Coin:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.radius = 12
        self.x = 0
        self.y = 0
        self.speed = 5
        self.weight = 1
        self.color = (255, 215, 0)
        self.reset()

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def reset(self):
        coin_type = random.choice([
            {"weight": 1, "color": (205, 127, 50)},   # bronze
            {"weight": 2, "color": (192, 192, 192)},  # silver
            {"weight": 3, "color": (255, 215, 0)},    # gold
        ])

        self.weight = coin_type["weight"]
        self.color = coin_type["color"]

        self.radius = 10 + self.weight * 3

        self.x = random.randint(70 + self.radius, self.screen_width - 70 - self.radius)
        self.y = random.randint(-500, -100)

    def update(self):
        # Move coin downward
        self.y += self.speed
        return self.y - self.radius > 600

    def draw(self, screen):
        # Draw coin
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 245, 180), (self.x, self.y), max(2, self.radius - 4))