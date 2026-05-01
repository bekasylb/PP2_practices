# Snake Game — TSIS 4

Advanced Snake game with PostgreSQL leaderboard, power-ups, obstacles, and polished screens.

## Requirements

```
pip install pygame psycopg2-binary
```

## PostgreSQL Setup

1. Create a database:
```sql
CREATE DATABASE snake_game;
```

2. The app auto-creates the tables on first launch via `db.init_db()`:
```sql
CREATE TABLE players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
```

3. Configure DB credentials in `config.py` or via environment variables:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=snake_game
DB_USER=postgres
DB_PASS=postgres
```

## Running

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| ↑ W | Move Up |
| ↓ S | Move Down |
| ← A | Move Left |
| → D | Move Right |
| P | Pause / Resume |
| ESC | Quit to Main Menu |

## File Structure

```
TSIS4/
├── main.py         # Entry point + all Pygame screens
├── game.py         # Snake, Food, PowerUp, GameState logic
├── db.py           # PostgreSQL integration (psycopg2)
├── settings.py     # JSON settings load/save
├── config.py       # Constants and configuration
├── settings.json   # User preferences (auto-created)
└── assets/         # (sounds/images if added)
```

## Features

- **Leaderboard** — PostgreSQL-backed Top 10, personal best tracking
- **Username entry** — typed at main menu, stored per-session
- **Poison food** — dark red; shortens snake by 2; game over if too short  
- **Power-ups** — Speed Boost ⚡, Slow Motion ❄, Shield 🛡 (each 5s, field life 8s)
- **Obstacles** — appear from Level 3, guaranteed not to trap snake
- **Settings** — snake color, grid overlay, sound; persisted in `settings.json`
- **4 Screens** — Main Menu, Gameplay, Game Over, Leaderboard, Settings
