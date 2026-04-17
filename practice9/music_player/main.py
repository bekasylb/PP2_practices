import pygame
from player import MusicPlayer


def draw_text(screen, text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 500))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 32)
    small_font = pygame.font.SysFont("Arial", 24)

    player = MusicPlayer("music")

    running = True
    while running:
        screen.fill((240, 240, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()

                elif event.key == pygame.K_s:
                    player.stop()

                elif event.key == pygame.K_n:
                    player.next_track()

                elif event.key == pygame.K_b:
                    player.previous_track()

                elif event.key == pygame.K_q:
                    running = False

        draw_text(screen, "Music Player", font, (0, 0, 0), 280, 40)
        draw_text(screen, f"Track: {player.get_current_track_name()}", small_font, (0, 0, 0), 80, 140)
        draw_text(screen, f"Status: {player.get_status()}", small_font, (0, 0, 0), 80, 190)
        draw_text(screen, f"Progress: {player.get_progress_seconds()} sec", small_font, (0, 0, 0), 80, 240)

        draw_text(screen, "Controls:", small_font, (0, 0, 0), 80, 320)
        draw_text(screen, "P = Play", small_font, (0, 0, 0), 80, 360)
        draw_text(screen, "S = Stop", small_font, (0, 0, 0), 80, 390)
        draw_text(screen, "N = Next", small_font, (0, 0, 0), 250, 360)
        draw_text(screen, "B = Previous", small_font, (0, 0, 0), 250, 390)
        draw_text(screen, "Q = Quit", small_font, (0, 0, 0), 500, 360)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
