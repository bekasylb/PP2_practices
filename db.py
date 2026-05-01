# db.py — PostgreSQL database integration via psycopg2

import os
import datetime

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("[db] psycopg2 not installed — leaderboard features disabled.")

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

# ── Schema SQL ────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""

# ── Connection helper ─────────────────────────────────────────────────────────

def _connect():
    """Return a new psycopg2 connection or None if unavailable."""
    if not PSYCOPG2_AVAILABLE:
        return None
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", DB_HOST),
            port=int(os.environ.get("DB_PORT", DB_PORT)),
            dbname=os.environ.get("DB_NAME", DB_NAME),
            user=os.environ.get("DB_USER", DB_USER),
            password=os.environ.get("DB_PASS", DB_PASS),
        )
        return conn
    except Exception as e:
        print(f"[db] Connection failed: {e}")
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist. Returns True on success."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
        return True
    except Exception as e:
        print(f"[db] init_db error: {e}")
        return False
    finally:
        conn.close()


def get_or_create_player(username: str) -> int | None:
    """Return player id, creating a row if needed."""
    conn = _connect()
    if conn is None:
        return None
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) "
                    "ON CONFLICT (username) DO NOTHING",
                    (username,),
                )
                cur.execute(
                    "SELECT id FROM players WHERE username = %s",
                    (username,),
                )
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        print(f"[db] get_or_create_player error: {e}")
        return None
    finally:
        conn.close()


def save_session(player_id: int, score: int, level_reached: int) -> bool:
    """Insert a new game session row."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (player_id, score, level_reached),
                )
        return True
    except Exception as e:
        print(f"[db] save_session error: {e}")
        return False
    finally:
        conn.close()


def get_personal_best(player_id: int) -> int:
    """Return the highest score ever achieved by this player (0 if none)."""
    conn = _connect()
    if conn is None:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions "
                "WHERE player_id = %s",
                (player_id,),
            )
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"[db] get_personal_best error: {e}")
        return 0
    finally:
        conn.close()


def get_top10() -> list[dict]:
    """
    Return top-10 all-time scores as a list of dicts:
    rank, username, score, level_reached, played_at (str)
    """
    conn = _connect()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    TO_CHAR(gs.played_at, 'YYYY-MM-DD') AS played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
                """
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"[db] get_top10 error: {e}")
        return []
    finally:
        conn.close()
