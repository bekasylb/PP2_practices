import pygame


class Snake:
    def __init__(self, start_x, start_y, block_size):
        self.body = [
            (start_x, start_y),
            (start_x - block_size, start_y),
            (start_x - block_size * 2, start_y),
        ]
        self.block_size = block_size
        self.direction = "RIGHT"
        self.grow_pending = 0

    def set_direction(self, new_direction):
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT",
        }

        if opposite[self.direction] != new_direction:
            self.direction = new_direction

    def move(self):
        head_x, head_y = self.body[0]

        if self.direction == "UP":
            head_y -= self.block_size
        elif self.direction == "DOWN":
            head_y += self.block_size
        elif self.direction == "LEFT":
            head_x -= self.block_size
        elif self.direction == "RIGHT":
            head_x += self.block_size

        new_head = (head_x, head_y)
        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1

    def get_head(self):
        return self.body[0]

    def collided_with_self(self):
        return self.body[0] in self.body[1:]

    def draw(self, screen):
        for i, (x, y) in enumerate(self.body):
            color = (0, 180, 0) if i == 0 else (0, 220, 0)
            pygame.draw.rect(
                screen,
                color,
                (x, y, self.block_size, self.block_size),
                border_radius=4
            )
