import random
import pygame


class Food:
    def __init__(self, block_size, grid_width, grid_height, wall_cells):
        self.block_size = block_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.wall_cells = wall_cells
        self.position = (0, 0)

    def respawn(self, snake_body):
        possible_positions = []

        for x in range(self.block_size, self.grid_width - self.block_size, self.block_size):
            for y in range(self.block_size, self.grid_height - self.block_size, self.block_size):
                pos = (x, y)
                if pos not in snake_body and pos not in self.wall_cells:
                    possible_positions.append(pos)

        self.position = random.choice(possible_positions)

    def draw(self, screen):
        x, y = self.position
        pygame.draw.rect(screen, (220, 50, 50), (x, y, self.block_size, self.block_size), border_radius=5)
