# main.py — Entry point; handles all Pygame screens

import sys
import math
import pygame

from config import *
from settings import load_settings, save_settings
from game import GameState, UP, DOWN, LEFT, RIGHT, cell_to_rect
import db


# ── Pygame init ───────────────────────────────────────────────────────────────

pygame.init()
screen  = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(TITLE)
clock   = pygame.time.Clock()

# Fonts
try:
    FONT_TITLE  = pygame.font.SysFont("consolas", 48, bold=True)
    FONT_LARGE  = pygame.font.SysFont("consolas", 32, bold=True)
    FONT_MEDIUM = pygame.font.SysFont("consolas", 22)
    FONT_SMALL  = pygame.font.SysFont("consolas", 16)
except Exception:
    FONT_TITLE  = pygame.font.Font(None, 60)
    FONT_LARGE  = pygame.font.Font(None, 40)
    FONT_MEDIUM = pygame.font.Font(None, 28)
    FONT_SMALL  = pygame.font.Font(None, 20)


# ── Utility helpers ───────────────────────────────────────────────────────────

def draw_text(surface, text, font, color, cx, cy):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(cx, cy))
    surface.blit(surf, rect)
    return rect


def draw_background(surface):
    surface.fill(DARK_BG)
    # Subtle scanline effect
    for y in range(0, WINDOW_HEIGHT, 4):
        pygame.draw.line(surface, (0, 0, 0, 20), (0, y), (WINDOW_WIDTH, y))


class Button:
    def __init__(self, text, cx, cy, w=220, h=46, color=GREEN, hover_color=None):
        self.text        = text
        self.rect        = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.color       = color
        self.hover_color = hover_color or tuple(min(255, c + 40) for c in color)
        self.hovered     = False

    def draw(self, surface):
        c = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, c, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=8)
        draw_text(surface, self.text, FONT_MEDIUM, BLACK, *self.rect.center)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Screens ───────────────────────────────────────────────────────────────────

# ── 1. Main Menu ──────────────────────────────────────────────────────────────

def screen_main_menu(settings: dict) -> tuple[str, str]:
    """Returns (action, username)  action in {'play','leaderboard','settings','quit'}"""
    username_input = ""
    cursor_visible = True
    cursor_timer   = 0
    error_msg      = ""

    btn_play        = Button("▶  PLAY",        WINDOW_WIDTH // 2, 360, 220, 50, GREEN)
    btn_leaderboard = Button("🏆  LEADERBOARD", WINDOW_WIDTH // 2, 420, 220, 50, GOLD)
    btn_settings    = Button("⚙  SETTINGS",    WINDOW_WIDTH // 2, 480, 220, 50, (100, 140, 220))
    btn_quit        = Button("✕  QUIT",         WINDOW_WIDTH // 2, 540, 220, 50, RED)
    buttons = [btn_play, btn_leaderboard, btn_settings, btn_quit]

    while True:
        dt_ms = clock.tick(FPS)
        cursor_timer += dt_ms
        if cursor_timer >= 500:
            cursor_timer = 0
            cursor_visible = not cursor_visible

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", ""

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username_input.strip():
                        return "play_direct", username_input.strip()
                    else:
                        error_msg = "Enter a username first!"
                elif event.key == pygame.K_BACKSPACE:
                    username_input = username_input[:-1]
                    error_msg = ""
                else:
                    ch = event.unicode
                    if ch.isprintable() and len(username_input) < 20:
                        username_input += ch
                        error_msg = ""

            for btn in buttons:
                if btn.clicked(event):
                    if btn is btn_play:
                        if username_input.strip():
                            return "play", username_input.strip()
                        else:
                            error_msg = "Enter a username first!"
                    elif btn is btn_leaderboard:
                        return "leaderboard", ""
                    elif btn is btn_settings:
                        return "settings", ""
                    elif btn is btn_quit:
                        return "quit", ""

        for btn in buttons:
            btn.update(mouse_pos)

        # Draw
        draw_background(screen)

        # Title
        t = pygame.time.get_ticks() / 1000
        glow = int(128 + 127 * math.sin(t * 1.5))
        draw_text(screen, "🐍  SNAKE GAME", FONT_TITLE, (0, glow, 100), WINDOW_WIDTH // 2, 100)
        draw_text(screen, "TSIS 4 — ADVANCED EDITION", FONT_SMALL, (80, 80, 120),
                  WINDOW_WIDTH // 2, 150)

        # Username box
        draw_text(screen, "USERNAME:", FONT_MEDIUM, SCORE_COLOR, WINDOW_WIDTH // 2, 225)
        box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 245, 300, 44)
        pygame.draw.rect(screen, PANEL_BG, box_rect, border_radius=6)
        pygame.draw.rect(screen, BORDER_COLOR, box_rect, 2, border_radius=6)
        display_text = username_input + ("|" if cursor_visible else " ")
        draw_text(screen, display_text, FONT_MEDIUM, WHITE, WINDOW_WIDTH // 2, 267)

        if error_msg:
            draw_text(screen, error_msg, FONT_SMALL, RED, WINDOW_WIDTH // 2, 305)

        draw_text(screen, "Press ENTER or click PLAY", FONT_SMALL, (60, 80, 100),
                  WINDOW_WIDTH // 2, 330)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()


# ── 2. Gameplay screen ────────────────────────────────────────────────────────

def screen_gameplay(settings: dict, username: str,
                    player_id: int | None, personal_best: int) -> dict:
    """Returns result dict: score, level, personal_best (updated)."""

    state = GameState(settings, player_id, personal_best)

    KEY_DIR = {
        pygame.K_UP: UP, pygame.K_w: UP,
        pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
        pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
        pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
    }

    paused = False

    while True:
        dt = clock.tick(FPS) / 1000.0  # seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    # Quit to main menu
                    return {"score": state.score, "level": state.level,
                            "personal_best": personal_best, "quit_early": True}
                elif event.key in KEY_DIR:
                    state.snake.set_direction(KEY_DIR[event.key])

        if not paused:
            result = state.update(dt)
            if result == "dead":
                # Auto-save to DB
                if player_id is not None:
                    db.save_session(player_id, state.score, state.level)
                    new_pb = db.get_personal_best(player_id)
                else:
                    new_pb = max(personal_best, state.score)
                return {"score": state.score, "level": state.level,
                        "personal_best": new_pb, "quit_early": False}

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_background(screen)

        # HUD panel
        pygame.draw.rect(screen, PANEL_BG, (0, 0, WINDOW_WIDTH, GRID_OFFSET_Y - 4))

        # Score / Level / PB / Power-up
        draw_text(screen, f"SCORE: {state.score}", FONT_MEDIUM, SCORE_COLOR, 120, 28)
        draw_text(screen, f"LEVEL: {state.level}",  FONT_MEDIUM, LEVEL_COLOR, 290, 28)
        draw_text(screen, f"BEST:  {state.personal_best}", FONT_MEDIUM, GOLD, 460, 28)

        # Speed / length
        spd = int(state._effective_speed())
        draw_text(screen, f"SPD:{spd}  LEN:{len(state.snake.body)}",
                  FONT_SMALL, (100, 120, 160), 650, 20)

        # Active power-up
        now = pygame.time.get_ticks()
        if state.active_effect:
            rem = max(0, (state.effect_end_ms - now) / 1000)
            colors = {"speed": POWERUP_SPEED_COLOR,
                      "slow":  POWERUP_SLOW_COLOR,
                      "shield": POWERUP_SHIELD_COLOR}
            c = colors.get(state.active_effect, WHITE)
            label = state.active_effect.upper()
            draw_text(screen, f"{label} {rem:.1f}s", FONT_SMALL, c, 650, 42)

        draw_text(screen, username, FONT_SMALL, (80, 80, 130), 650, 58)

        # Play area border
        area = pygame.Rect(GRID_OFFSET_X - 2, GRID_OFFSET_Y - 2,
                           GRID_COLS * CELL_SIZE + 4,
                           GRID_ROWS * CELL_SIZE + 4)
        pygame.draw.rect(screen, BORDER_COLOR, area, 2, border_radius=4)

        state.draw(screen)

        if paused:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "PAUSED — Press P to resume", FONT_LARGE, WHITE,
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        pygame.display.flip()


# ── 3. Game Over screen ───────────────────────────────────────────────────────

def screen_game_over(result: dict, username: str) -> str:
    """Returns 'retry' or 'menu'."""
    btn_retry = Button("↺  RETRY",     WINDOW_WIDTH // 2 - 130, 440, 200, 50, GREEN)
    btn_menu  = Button("⌂  MAIN MENU", WINDOW_WIDTH // 2 + 130, 440, 200, 50, (100, 140, 220))

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.clicked(event): return "retry"
            if btn_menu.clicked(event):  return "menu"

        btn_retry.update(mouse_pos)
        btn_menu.update(mouse_pos)

        draw_background(screen)
        draw_text(screen, "GAME  OVER", FONT_TITLE, RED, WINDOW_WIDTH // 2, 150)
        draw_text(screen, f"Player: {username}", FONT_MEDIUM, WHITE, WINDOW_WIDTH // 2, 230)
        draw_text(screen, f"Final Score:  {result['score']}", FONT_LARGE, SCORE_COLOR,
                  WINDOW_WIDTH // 2, 285)
        draw_text(screen, f"Level Reached: {result['level']}", FONT_LARGE, LEVEL_COLOR,
                  WINDOW_WIDTH // 2, 335)
        draw_text(screen, f"Personal Best: {result['personal_best']}", FONT_LARGE, GOLD,
                  WINDOW_WIDTH // 2, 385)

        btn_retry.draw(screen)
        btn_menu.draw(screen)
        pygame.display.flip()


# ── 4. Leaderboard screen ─────────────────────────────────────────────────────

def screen_leaderboard() -> None:
    btn_back = Button("← BACK", WINDOW_WIDTH // 2, 590, 160, 44, (100, 140, 220))
    rows = db.get_top10()

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if btn_back.clicked(event):
                return

        btn_back.update(mouse_pos)
        draw_background(screen)

        draw_text(screen, "🏆  LEADERBOARD", FONT_TITLE, GOLD, WINDOW_WIDTH // 2, 55)

        # Table header
        hx = [60, 140, 360, 520, 650]
        headers = ["#", "USERNAME", "SCORE", "LEVEL", "DATE"]
        hcolors = [GOLD, WHITE, SCORE_COLOR, LEVEL_COLOR, (140, 140, 180)]
        for x, h, c in zip(hx, headers, hcolors):
            s = FONT_SMALL.render(h, True, c)
            screen.blit(s, (x, 110))

        pygame.draw.line(screen, BORDER_COLOR, (50, 130), (750, 130), 1)

        if not rows:
            draw_text(screen, "No scores yet — database may be offline.",
                      FONT_MEDIUM, (100, 100, 140), WINDOW_WIDTH // 2, 300)
        else:
            for i, row in enumerate(rows):
                y = 148 + i * 36
                # Alternating row bg
                if i % 2 == 0:
                    pygame.draw.rect(screen, (25, 25, 40), (50, y - 4, 700, 32))

                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(int(row["rank"]), "  ")
                vals = [
                    f"{medal}{row['rank']}",
                    str(row["username"])[:16],
                    str(row["score"]),
                    str(row["level_reached"]),
                    str(row["played_at"]),
                ]
                for x, v, c in zip(hx, vals, hcolors):
                    s = FONT_SMALL.render(v, True, c)
                    screen.blit(s, (x, y))

        btn_back.draw(screen)
        pygame.display.flip()


# ── 5. Settings screen ────────────────────────────────────────────────────────

def screen_settings(settings: dict) -> dict:
    """Returns (possibly mutated) settings dict."""
    s = dict(settings)

    # Color presets
    color_presets = [
        ("Green",   [0,   220, 120]),
        ("Cyan",    [0,   220, 220]),
        ("Orange",  [255, 140, 0]),
        ("Pink",    [255, 80,  180]),
        ("Yellow",  [240, 220, 0]),
        ("White",   [220, 220, 220]),
    ]
    selected_preset = 0
    # Try to match existing
    for i, (_, rgb) in enumerate(color_presets):
        if rgb == list(s.get("snake_color", [0, 220, 120])):
            selected_preset = i

    btn_save = Button("💾  SAVE & BACK", WINDOW_WIDTH // 2, 560, 240, 50, GREEN)

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return settings   # discard changes
            if btn_save.clicked(event):
                s["snake_color"] = color_presets[selected_preset][1]
                save_settings(s)
                return s

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Grid toggle button area
                if grid_rect.collidepoint(event.pos):
                    s["grid_overlay"] = not s.get("grid_overlay", True)
                # Sound toggle
                if sound_rect.collidepoint(event.pos):
                    s["sound"] = not s.get("sound", True)
                # Color swatches
                for idx, rect in enumerate(swatch_rects):
                    if rect.collidepoint(event.pos):
                        selected_preset = idx

        btn_save.update(mouse_pos)
        draw_background(screen)

        draw_text(screen, "⚙  SETTINGS", FONT_TITLE, (100, 140, 220), WINDOW_WIDTH // 2, 55)

        # Grid toggle
        grid_label = "Grid Overlay:"
        grid_state = "ON" if s.get("grid_overlay", True) else "OFF"
        grid_color = GREEN if s.get("grid_overlay", True) else RED
        draw_text(screen, grid_label, FONT_MEDIUM, WHITE, WINDOW_WIDTH // 2 - 100, 170)
        grid_rect = pygame.Rect(WINDOW_WIDTH // 2 + 60, 155, 80, 32)
        pygame.draw.rect(screen, grid_color, grid_rect, border_radius=6)
        draw_text(screen, grid_state, FONT_MEDIUM, BLACK, grid_rect.centerx, grid_rect.centery)

        # Sound toggle
        sound_label = "Sound Effects:"
        sound_state = "ON" if s.get("sound", True) else "OFF"
        sound_color = GREEN if s.get("sound", True) else RED
        draw_text(screen, sound_label, FONT_MEDIUM, WHITE, WINDOW_WIDTH // 2 - 100, 235)
        sound_rect = pygame.Rect(WINDOW_WIDTH // 2 + 60, 220, 80, 32)
        pygame.draw.rect(screen, sound_color, sound_rect, border_radius=6)
        draw_text(screen, sound_state, FONT_MEDIUM, BLACK, sound_rect.centerx, sound_rect.centery)

        # Color picker
        draw_text(screen, "Snake Color:", FONT_MEDIUM, WHITE, WINDOW_WIDTH // 2 - 100, 305)
        swatch_rects = []
        sw_start_x = WINDOW_WIDTH // 2 - (len(color_presets) * 46) // 2
        for idx, (name, rgb) in enumerate(color_presets):
            sw_x = sw_start_x + idx * 46
            sw_rect = pygame.Rect(sw_x, 330, 38, 38)
            swatch_rects.append(sw_rect)
            pygame.draw.rect(screen, tuple(rgb), sw_rect, border_radius=5)
            if idx == selected_preset:
                pygame.draw.rect(screen, WHITE, sw_rect, 3, border_radius=5)
            draw_text(screen, name, FONT_SMALL, (140, 140, 180), sw_rect.centerx, 380)

        # Preview snake segment
        preview_color = tuple(color_presets[selected_preset][1])
        pr = pygame.Rect(WINDOW_WIDTH // 2 - 80, 410, 160, 24)
        pygame.draw.rect(screen, preview_color, pr, border_radius=4)
        draw_text(screen, "preview", FONT_SMALL, BLACK, WINDOW_WIDTH // 2, 422)

        btn_save.draw(screen)
        pygame.display.flip()


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    db.init_db()
    settings = load_settings()

    username  = ""
    player_id = None
    personal_best = 0

    while True:
        action, uname = screen_main_menu(settings)

        if action == "quit":
            break

        if action == "leaderboard":
            screen_leaderboard()
            continue

        if action == "settings":
            settings = screen_settings(settings)
            continue

        if action in ("play", "play_direct"):
            username  = uname
            player_id = db.get_or_create_player(username)
            if player_id is not None:
                personal_best = db.get_personal_best(player_id)
            else:
                personal_best = 0

            # Game loop (supports retry without returning to main menu)
            retry = True
            while retry:
                result = screen_gameplay(settings, username, player_id, personal_best)
                personal_best = result["personal_best"]

                if result.get("quit_early"):
                    retry = False
                    continue

                outcome = screen_game_over(result, username)
                retry = (outcome == "retry")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
