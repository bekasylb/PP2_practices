# game.py — Core game logic: Snake, Food, Power-ups, Obstacles

import random
import pygame
import math
from config import *


# ── Direction constants ───────────────────────────────────────────────────────
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


# ── Helper ────────────────────────────────────────────────────────────────────

def random_cell(exclude: set) -> tuple[int, int]:
    """Pick a random grid cell not in exclude."""
    while True:
        c = random.randint(0, GRID_COLS - 1)
        r = random.randint(0, GRID_ROWS - 1)
        if (c, r) not in exclude:
            return (c, r)


def cell_to_rect(col: int, row: int) -> pygame.Rect:
    """Convert grid coordinate to pixel Rect."""
    x = GRID_OFFSET_X + col * CELL_SIZE
    y = GRID_OFFSET_Y + row * CELL_SIZE
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)


# ── Food ──────────────────────────────────────────────────────────────────────

class Food:
    def __init__(self, pos, kind="normal"):
        self.pos   = pos   # (col, row)
        self.kind  = kind  # 'normal', 'bonus', 'poison'
        self.spawn_time = pygame.time.get_ticks()

    @property
    def color(self):
        if self.kind == "bonus":
            return FOOD2_COLOR
        if self.kind == "poison":
            return POISON_COLOR
        return FOOD_COLOR

    @property
    def points(self):
        return FOOD_WEIGHTS.get(self.kind, 1)

    def is_expired(self):
        elapsed = (pygame.time.get_ticks() - self.spawn_time) / 1000
        return elapsed > FOOD_TIMER_SECONDS

    def draw(self, surface):
        r = cell_to_rect(*self.pos)
        # Pulsing alpha effect
        t = pygame.time.get_ticks() / 300
        factor = 0.75 + 0.25 * math.sin(t)
        c = tuple(int(ch * factor) for ch in self.color)
        pygame.draw.rect(surface, c, r.inflate(-2, -2), border_radius=4)


# ── Power-up ──────────────────────────────────────────────────────────────────

class PowerUp:
    def __init__(self, pos, kind):
        self.pos        = pos
        self.kind       = kind   # 'speed', 'slow', 'shield'
        self.spawn_time = pygame.time.get_ticks()

    @property
    def color(self):
        return {
            "speed":  POWERUP_SPEED_COLOR,
            "slow":   POWERUP_SLOW_COLOR,
            "shield": POWERUP_SHIELD_COLOR,
        }[self.kind]

    @property
    def label(self):
        return {"speed": "⚡", "slow": "❄", "shield": "🛡"}[self.kind]

    def is_expired(self):
        return (pygame.time.get_ticks() - self.spawn_time) > POWERUP_FIELD_LIFE_MS

    def draw(self, surface):
        r = cell_to_rect(*self.pos)
        pygame.draw.rect(surface, self.color, r.inflate(-4, -4), border_radius=5)
        pygame.draw.rect(surface, WHITE, r.inflate(-4, -4), 1, border_radius=5)


# ── Snake ─────────────────────────────────────────────────────────────────────

class Snake:
    def __init__(self, start_col, start_row, snake_color):
        self.body      = [(start_col - i, start_row) for i in range(INITIAL_LENGTH)]
        self.direction = RIGHT
        self.next_dir  = RIGHT
        self.alive     = True
        self.color     = snake_color          # RGB tuple
        self.shield    = False                # power-up state

    @property
    def head(self):
        return self.body[0]

    def set_direction(self, new_dir):
        if new_dir != OPPOSITE.get(self.direction):
            self.next_dir = new_dir

    def move(self) -> tuple[int, int]:
        """Advance one step. Returns new head position."""
        self.direction = self.next_dir
        dc, dr = self.direction
        new_head = (self.head[0] + dc, self.head[1] + dr)
        self.body.insert(0, new_head)
        tail = self.body.pop()
        return new_head, tail

    def grow(self, segments=1):
        """Append segments at the tail end."""
        for _ in range(segments):
            self.body.append(self.body[-1])

    def shorten(self, segments=2):
        """Remove tail segments. Returns False if too short."""
        for _ in range(segments):
            if len(self.body) > 1:
                self.body.pop()
        return len(self.body) > 1

    def occupies(self) -> set:
        return set(self.body)

    def draw(self, surface):
        for i, (col, row) in enumerate(self.body):
            r = cell_to_rect(col, row)
            color = self.color if i > 0 else tuple(
                min(255, ch + 60) for ch in self.color
            )
            pygame.draw.rect(surface, color, r.inflate(-1, -1), border_radius=3)
            if i == 0 and self.shield:
                pygame.draw.rect(surface, POWERUP_SHIELD_COLOR,
                                 r.inflate(-1, -1), 2, border_radius=3)


# ── Game state ────────────────────────────────────────────────────────────────

class GameState:
    """Encapsulates one round of gameplay."""

    def __init__(self, settings: dict, player_id: int | None, personal_best: int):
        self.settings      = settings
        self.player_id     = player_id
        self.personal_best = personal_best

        snake_color = tuple(settings.get("snake_color", SNAKE_HEAD_COLOR))
        mid_col = GRID_COLS // 2
        mid_row = GRID_ROWS // 2
        self.snake = Snake(mid_col, mid_row, snake_color)

        self.score    = 0
        self.level    = 1
        self.food_eaten_this_level = 0

        # Speed
        self.base_speed   = INITIAL_SPEED
        self.current_speed = self.base_speed  # cells/sec
        self._move_accum   = 0.0              # fractional ticks

        # Food items on field (list of Food)
        self.foods: list[Food] = []

        # Power-ups
        self.field_powerup: PowerUp | None = None
        self.active_effect: str | None = None   # 'speed', 'slow', 'shield'
        self.effect_end_ms: int = 0
        self._next_powerup_ms: int = pygame.time.get_ticks() + random.randint(5000, 12000)

        # Obstacles (set of (col, row))
        self.obstacles: set = set()

        # Spawn first food
        self._spawn_food()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _occupied(self) -> set:
        """All cells that are off-limits for spawning."""
        return self.snake.occupies() | self.obstacles | {f.pos for f in self.foods} | (
            {self.field_powerup.pos} if self.field_powerup else set()
        )

    def _spawn_food(self):
        """Spawn a new food item; type determined by chance."""
        pos = random_cell(self._occupied())
        r = random.random()
        if r < POISON_FOOD_CHANCE:
            kind = "poison"
        elif r < POISON_FOOD_CHANCE + BONUS_FOOD_CHANCE:
            kind = "bonus"
        else:
            kind = "normal"
        self.foods.append(Food(pos, kind))

    def _spawn_powerup(self):
        if self.field_powerup is not None:
            return
        pos  = random_cell(self._occupied())
        kind = random.choice(["speed", "slow", "shield"])
        self.field_powerup = PowerUp(pos, kind)

    def _place_obstacles(self):
        """Add OBSTACLES_PER_LEVEL blocks, avoiding snake proximity."""
        avoid = self._occupied()
        # Keep a safety zone around snake head
        hc, hr = self.snake.head
        for dc in range(-3, 4):
            for dr in range(-3, 4):
                avoid.add((hc + dc, hr + dr))
        count = 0
        attempts = 0
        while count < OBSTACLES_PER_LEVEL and attempts < 500:
            attempts += 1
            pos = random_cell(avoid)
            self.obstacles.add(pos)
            avoid.add(pos)
            count += 1

    def _apply_powerup(self, kind: str):
        now = pygame.time.get_ticks()
        if kind == "shield":
            self.snake.shield = True
            self.active_effect = "shield"
            self.effect_end_ms = now + POWERUP_DURATION_MS
        elif kind == "speed":
            self.active_effect = "speed"
            self.effect_end_ms = now + POWERUP_DURATION_MS
        elif kind == "slow":
            self.active_effect = "slow"
            self.effect_end_ms = now + POWERUP_DURATION_MS

    def _effective_speed(self) -> float:
        s = self.base_speed + (self.level - 1) * SPEED_INCREMENT
        s = min(s, MAX_SPEED)
        if self.active_effect == "speed":
            s *= SPEED_BOOST_FACTOR
        elif self.active_effect == "slow":
            s *= SLOW_MOTION_FACTOR
        return s

    def _advance_level(self):
        self.level += 1
        self.food_eaten_this_level = 0
        self.base_speed = min(INITIAL_SPEED + (self.level - 1) * SPEED_INCREMENT, MAX_SPEED)
        if self.level >= OBSTACLE_LEVEL_START:
            self._place_obstacles()

    # ── Public update ─────────────────────────────────────────────────────────

    def update(self, dt: float) -> str:
        """
        dt: seconds since last frame.
        Returns 'running', 'dead'.
        """
        now = pygame.time.get_ticks()

        # Expire active power-up effect
        if self.active_effect and now >= self.effect_end_ms:
            if self.active_effect == "shield":
                self.snake.shield = False
            self.active_effect = None

        # Expire field power-up
        if self.field_powerup and self.field_powerup.is_expired():
            self.field_powerup = None

        # Expire foods
        self.foods = [f for f in self.foods if not f.is_expired()]
        if not self.foods:
            self._spawn_food()

        # Spawn power-up periodically
        if self.field_powerup is None and now >= self._next_powerup_ms:
            self._spawn_powerup()
            self._next_powerup_ms = now + random.randint(8000, 20000)

        # Accumulate movement ticks
        speed = self._effective_speed()
        self._move_accum += dt * speed

        if self._move_accum < 1.0:
            return "running"

        self._move_accum -= 1.0

        # Move snake
        new_head, _ = self.snake.move()
        col, row = new_head

        # Wall collision
        if col < 0 or col >= GRID_COLS or row < 0 or row >= GRID_ROWS:
            if self.snake.shield:
                self.snake.shield = False
                self.active_effect = None
                # Push back to opposite border
                col = col % GRID_COLS
                row = row % GRID_ROWS
                self.snake.body[0] = (col, row)
            else:
                self.snake.alive = False
                return "dead"

        # Self-collision (skip head)
        if new_head in self.snake.body[1:]:
            if self.snake.shield:
                self.snake.shield = False
                self.active_effect = None
            else:
                self.snake.alive = False
                return "dead"

        # Obstacle collision
        if new_head in self.obstacles:
            if self.snake.shield:
                self.snake.shield = False
                self.active_effect = None
                # Undo the move — push back
                self.snake.body[0] = self.snake.body[1]
            else:
                self.snake.alive = False
                return "dead"

        # Food collision
        eaten = [f for f in self.foods if f.pos == new_head]
        for food in eaten:
            self.foods.remove(food)
            if food.kind == "poison":
                survived = self.snake.shorten(2)
                if not survived:
                    self.snake.alive = False
                    return "dead"
            else:
                self.score += food.points * self.level
                self.snake.grow(1)
                self.food_eaten_this_level += 1
                if self.food_eaten_this_level >= FOOD_PER_LEVEL:
                    self._advance_level()
            self._spawn_food()

        # Power-up collision
        if self.field_powerup and self.field_powerup.pos == new_head:
            self._apply_powerup(self.field_powerup.kind)
            self.field_powerup = None

        return "running"

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        # Grid overlay
        if self.settings.get("grid_overlay", True):
            for c in range(GRID_COLS):
                for r in range(GRID_ROWS):
                    rect = cell_to_rect(c, r)
                    pygame.draw.rect(surface, GRID_COLOR, rect, 1)

        # Obstacles
        for (oc, or_) in self.obstacles:
            r = cell_to_rect(oc, or_)
            pygame.draw.rect(surface, OBSTACLE_COLOR, r, border_radius=2)
            pygame.draw.rect(surface, (50, 50, 70), r, 1, border_radius=2)

        # Food
        for food in self.foods:
            food.draw(surface)

        # Power-up
        if self.field_powerup:
            self.field_powerup.draw(surface)

        # Snake
        self.snake.draw(surface)
