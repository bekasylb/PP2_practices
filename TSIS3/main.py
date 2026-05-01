import pygame

from racer import RacerGame

from ui import (
    Button,
    draw_centered_text,
    draw_text,
    get_username_input,
)
from persistence import (
    load_settings,
    save_settings,
    load_leaderboard,
)

pygame.init()

WIDTH = 500
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer")
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("Arial", 42, bold=True)
FONT = pygame.font.SysFont("Arial", 28)
SMALL_FONT = pygame.font.SysFont("Arial", 22)


def run_settings_screen(screen, clock, settings):
    buttons = {
        "sound": Button(150, 220, 200, 50, "Sound"),
        "color": Button(150, 300, 200, 50, "Car Color"),
        "difficulty": Button(150, 380, 200, 50, "Difficulty"),
        "back": Button(150, 500, 200, 50, "Back"),
    }

    color_options = ["blue", "red", "green", "yellow"]
    difficulty_options = ["easy", "medium", "hard"]

    running = True
    while running:
        screen.fill((20, 20, 30))
        draw_centered_text(screen, "Settings", TITLE_FONT, (255, 255, 255), WIDTH // 2, 100)

        draw_text(screen, f"Sound: {'ON' if settings['sound'] else 'OFF'}", FONT, (255, 255, 255), 150, 180)
        draw_text(screen, f"Car Color: {settings['car_color']}", FONT, (255, 255, 255), 150, 260)
        draw_text(screen, f"Difficulty: {settings['difficulty']}", FONT, (255, 255, 255), 150, 340)

        for button in buttons.values():
            button.draw(screen, FONT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if buttons["sound"].is_clicked(mx, my):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                elif buttons["color"].is_clicked(mx, my):
                    current_index = color_options.index(settings["car_color"])
                    settings["car_color"] = color_options[(current_index + 1) % len(color_options)]
                    save_settings(settings)

                elif buttons["difficulty"].is_clicked(mx, my):
                    current_index = difficulty_options.index(settings["difficulty"])
                    settings["difficulty"] = difficulty_options[(current_index + 1) % len(difficulty_options)]
                    save_settings(settings)

                elif buttons["back"].is_clicked(mx, my):
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


def run_leaderboard_screen(screen, clock):
    back_button = Button(170, 700, 160, 50, "Back")

    running = True
    while running:
        leaderboard = load_leaderboard()

        screen.fill((15, 15, 25))
        draw_centered_text(screen, "Top 10 Leaderboard", TITLE_FONT, (255, 255, 255), WIDTH // 2, 70)

        y = 140
        if leaderboard:
            for index, entry in enumerate(leaderboard[:10], start=1):
                text = f"{index}. {entry['name']}  |  Score: {entry['score']}  |  Dist: {entry['distance']}"
                draw_text(screen, text, SMALL_FONT, (240, 240, 240), 30, y)
                y += 45
        else:
            draw_centered_text(screen, "No scores yet", FONT, (220, 220, 220), WIDTH // 2, 250)

        back_button.draw(screen, FONT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if back_button.is_clicked(mx, my):
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


def run_game_over_screen(screen, clock, result):
    retry_button = Button(150, 560, 200, 50, "Retry")
    menu_button = Button(150, 630, 200, 50, "Main Menu")

    running = True
    while running:
        screen.fill((25, 10, 10))
        draw_centered_text(screen, "Game Over", TITLE_FONT, (255, 100, 100), WIDTH // 2, 120)

        draw_centered_text(screen, f"Score: {result['score']}", FONT, (255, 255, 255), WIDTH // 2, 240)
        draw_centered_text(screen, f"Distance: {result['distance']}", FONT, (255, 255, 255), WIDTH // 2, 290)
        draw_centered_text(screen, f"Coins: {result['coins']}", FONT, (255, 255, 255), WIDTH // 2, 340)

        retry_button.draw(screen, FONT)
        menu_button.draw(screen, FONT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if retry_button.is_clicked(mx, my):
                    return "retry"
                if menu_button.is_clicked(mx, my):
                    return "menu"

        pygame.display.flip()
        clock.tick(60)


def run_main_menu(screen, clock):
    buttons = {
        "play": Button(150, 250, 200, 50, "Play"),
        "leaderboard": Button(150, 330, 200, 50, "Leaderboard"),
        "settings": Button(150, 410, 200, 50, "Settings"),
        "quit": Button(150, 490, 200, 50, "Quit"),
    }

    running = True
    while running:
        screen.fill((18, 18, 28))
        draw_centered_text(screen, "TSIS3 Racer", TITLE_FONT, (255, 255, 255), WIDTH // 2, 140)

        for button in buttons.values():
            button.draw(screen, FONT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if buttons["play"].is_clicked(mx, my):
                    return "play"
                if buttons["leaderboard"].is_clicked(mx, my):
                    return "leaderboard"
                if buttons["settings"].is_clicked(mx, my):
                    return "settings"
                if buttons["quit"].is_clicked(mx, my):
                    return "quit"

        pygame.display.flip()
        clock.tick(60)


def main():
    settings = load_settings()
    state = "menu"

    while True:
        if state == "menu":
            state = run_main_menu(screen, clock)

        elif state == "settings":
            state = run_settings_screen(screen, clock, settings)

        elif state == "leaderboard":
            state = run_leaderboard_screen(screen, clock)

        elif state == "play":
            player_name = get_username_input(screen, clock, WIDTH, HEIGHT)
            if player_name is None:
                state = "menu"
                continue

            game = RacerGame(screen, clock, settings, player_name)
            result = game.run()

            if result == "quit":
                break

            state = run_game_over_screen(screen, clock, result)

        elif state == "retry":
            state = "play"

        elif state == "quit":
            break

    pygame.quit()


if __name__ == "__main__":
    main()