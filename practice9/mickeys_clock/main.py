import pygame
from clock import MickeyClock


def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Mickey Clock")

    app = MickeyClock(screen)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        app.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
