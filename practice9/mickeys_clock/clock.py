import pygame
from datetime import datetime
import math


class MickeyClock:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.center = (self.width // 2, self.height // 2)

        self.background = pygame.image.load("images/mickeyclock.jpeg").convert()
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

    def draw_hand_line(self, angle, length, width):
        rad = math.radians(angle - 90)
        end_x = self.center[0] + length * math.cos(rad)
        end_y = self.center[1] + length * math.sin(rad)

        pygame.draw.line(
            self.screen,
            (0, 0, 0),
            self.center,
            (end_x, end_y),
            width
        )

    def update(self):
        self.screen.blit(self.background, (0, 0))

        now = datetime.now()
        minutes = now.minute
        seconds = now.second

        minute_angle = minutes * 6
        second_angle = seconds * 6

        # Минутная стрелка
        self.draw_hand_line(minute_angle, 140, 6)

        # Секундная стрелка
        self.draw_hand_line(second_angle, 170, 3)

        pygame.draw.circle(self.screen, (0, 0, 0), self.center, 8)
