# config.py — Game constants and configuration

# Window
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 640
TITLE         = "Snake Game — TSIS 4"
FPS           = 60

# Grid
CELL_SIZE      = 20
GRID_COLS      = (WINDOW_WIDTH  - 40) // CELL_SIZE   # 38
GRID_ROWS      = (WINDOW_HEIGHT - 100) // CELL_SIZE  # 27
GRID_OFFSET_X  = 20
GRID_OFFSET_Y  = 80

# Colors (defaults; snake color can be overridden by settings)
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
DARK_BG      = (15,  15,  25)
PANEL_BG     = (20,  20,  35)
GRID_COLOR   = (30,  30,  45)
BORDER_COLOR = (60,  60,  90)

SNAKE_HEAD_COLOR   = (0,   220, 120)
SNAKE_BODY_COLOR   = (0,   180, 90)
FOOD_COLOR         = (255, 80,  60)
FOOD2_COLOR        = (255, 160, 0)    # higher-point food
POISON_COLOR       = (120, 0,   30)   # dark red/maroon
OBSTACLE_COLOR     = (80,  80,  100)

POWERUP_SPEED_COLOR = (255, 220, 0)   # yellow
POWERUP_SLOW_COLOR  = (100, 180, 255) # light blue
POWERUP_SHIELD_COLOR= (180, 100, 255) # purple

SCORE_COLOR  = (200, 200, 255)
LEVEL_COLOR  = (100, 255, 200)
RED          = (220, 60,  60)
GREEN        = (60,  220, 100)
GOLD         = (255, 200, 50)

# Gameplay
INITIAL_SPEED    = 8          # cells/sec (FPS ticks per move = FPS/INITIAL_SPEED)
SPEED_INCREMENT  = 1          # added per level
MAX_SPEED        = 20
FOOD_PER_LEVEL   = 5          # food eaten to advance a level
INITIAL_LENGTH   = 3

# Food weights (points)
FOOD_WEIGHTS = {
    'normal':  1,
    'bonus':   3,
    'poison': -2,   # handled separately (shorten snake)
}
FOOD_TIMER_SECONDS = 8        # disappears after this
BONUS_FOOD_CHANCE  = 0.25     # probability to spawn bonus food
POISON_FOOD_CHANCE = 0.15

# Power-ups
POWERUP_DURATION_MS   = 5_000  # 5 s effect
POWERUP_FIELD_LIFE_MS = 8_000  # disappears if not collected
SPEED_BOOST_FACTOR    = 1.6
SLOW_MOTION_FACTOR    = 0.5

# Obstacles
OBSTACLE_LEVEL_START = 3
OBSTACLES_PER_LEVEL  = 4      # new blocks per level (additive)

# DB (override via environment variables in production)
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "snake_game"
DB_USER = "postgres"
DB_PASS = "postgres"
