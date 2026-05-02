import random
import pygame


class Food:
    def __init__(self, block_size, grid_width, grid_height, wall_cells):
        self.block_size = block_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.wall_cells = wall_cells

        self.position = (0, 0)
        self.weight = 1
        self.color = (220, 50, 50)
        self.spawn_time = 0
        self.life_time = 5000  # milliseconds

    def respawn(self, snake_body):
        food_type = random.choice([
            {"weight": 1, "color": (220, 50, 50), "life_time": 7000},
            {"weight": 2, "color": (255, 165, 0), "life_time": 5000},
            {"weight": 3, "color": (255, 215, 0), "life_time": 3500},
        ])

        self.weight = food_type["weight"]
        self.color = food_type["color"]
        self.life_time = food_type["life_time"]

        possible_positions = []

        for x in range(self.block_size, self.grid_width - self.block_size, self.block_size):
            for y in range(self.block_size, self.grid_height - self.block_size, self.block_size):
                pos = (x, y)
                if pos not in snake_body and pos not in self.wall_cells:
                    possible_positions.append(pos)

        self.position = random.choice(possible_positions)
        self.spawn_time = pygame.time.get_ticks()

    def expired(self):
        # Check if food should disappear
        return pygame.time.get_ticks() - self.spawn_time > self.life_time

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, self.color, (x, y, self.block_size, self.block_size), border_radius=5)