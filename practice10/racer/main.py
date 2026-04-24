import pygame
from player import Player
from enemy import Enemy
from coin import Coin


WIDTH = 400
HEIGHT = 600


def draw_road(screen, line_offset):
    screen.fill((80, 170, 80))

    pygame.draw.rect(screen, (60, 60, 60), (50, 0, 300, HEIGHT))

    pygame.draw.line(screen, (255, 255, 255), (50, 0), (50, HEIGHT), 4)
    pygame.draw.line(screen, (255, 255, 255), (350, 0), (350, HEIGHT), 4)

    dash_height = 40
    gap = 20
    y = -line_offset

    while y < HEIGHT:
        pygame.draw.rect(screen, (255, 255, 255), (195, y, 10, dash_height))
        y += dash_height + gap


def game_over_screen(screen, font_big, font_small, score, coins):
    screen.fill((20, 20, 20))

    game_over_text = font_big.render("GAME OVER", True, (255, 80, 80))
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))
    coins_text = font_small.render(f"Coins: {coins}", True, (255, 255, 255))
    info_text = font_small.render("Press R to restart or Q to quit", True, (200, 200, 200))

    screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 200)))
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 280)))
    screen.blit(coins_text, coins_text.get_rect(center=(WIDTH // 2, 320)))
    screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, 400)))


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racer")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    font_big = pygame.font.SysFont("Arial", 42, bold=True)
    font_small = pygame.font.SysFont("Arial", 26)

    def create_game():
        player = Player(WIDTH // 2 - 25, HEIGHT - 120, 50, 90, WIDTH, HEIGHT)
        enemies = [Enemy(WIDTH), Enemy(WIDTH)]
        enemies[1].rect.y = -350
        coin = Coin(WIDTH)
        score = 0
        coins_collected = 0
        speed = 5
        line_offset = 0
        game_over = False
        return player, enemies, coin, score, coins_collected, speed, line_offset, game_over

    player, enemies, coin, score, coins_collected, speed, line_offset, game_over = create_game()

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player, enemies, coin, score, coins_collected, speed, line_offset, game_over = create_game()
                elif event.key == pygame.K_q:
                    running = False

        if not game_over:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_q]:
                running = False

            player.move(keys)

            line_offset = (line_offset + speed) % 60
            draw_road(screen, line_offset)

            for enemy in enemies:
                if enemy.update(speed):
                    enemy.reset()
                    score += 1

                enemy.draw(screen)

                if player.rect.colliderect(enemy.rect):
                    game_over = True

            coin.speed = speed
            if coin.update():
                coin.reset()

            if player.rect.colliderect(coin.rect):
                coins_collected += 1
                coin.reset()

            coin.draw(screen)

            speed = 5 + score // 5

            #Draw player
            player.draw(screen)

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (20, 20))

            coin_text = font.render(f"Coins: {coins_collected}", True, (255, 255, 0))
            coin_rect = coin_text.get_rect(topright=(WIDTH - 20, 20))
            screen.blit(coin_text, coin_rect)

        else:
            game_over_screen(screen, font_big, font_small, score, coins_collected)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
