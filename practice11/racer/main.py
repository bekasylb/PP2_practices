import pygame
from player import Player
from enemy import Enemy
from coin import Coin

WIDTH = 400
HEIGHT = 600
COINS_TO_INCREASE_SPEED = 10


def draw_road(screen, line_offset):
    # Grass
    screen.fill((80, 170, 80))

    # Road
    pygame.draw.rect(screen, (60, 60, 60), (50, 0, 300, HEIGHT))

    # Road borders
    pygame.draw.line(screen, (255, 255, 255), (50, 0), (50, HEIGHT), 4)
    pygame.draw.line(screen, (255, 255, 255), (350, 0), (350, HEIGHT), 4)

    # Moving dashed center line
    dash_height = 40
    gap = 20
    y = -line_offset

    while y < HEIGHT:
        pygame.draw.rect(screen, (255, 255, 255), (195, y, 10, dash_height))
        y += dash_height + gap


def game_over_screen(screen, font_big, font_small, score, coin_score):
    screen.fill((20, 20, 20))

    game_over_text = font_big.render("GAME OVER", True, (255, 80, 80))
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))
    coins_text = font_small.render(f"Coins value: {coin_score}", True, (255, 255, 0))
    info_text = font_small.render("Press R to restart or Q to quit", True, (210, 210, 210))

    screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 200)))
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 280)))
    screen.blit(coins_text, coins_text.get_rect(center=(WIDTH // 2, 320)))
    screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, 400)))


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Practice11 Racer")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    font_big = pygame.font.SysFont("Arial", 40, bold=True)
    font_small = pygame.font.SysFont("Arial", 26)

    def create_game():
        player = Player(WIDTH // 2 - 25, HEIGHT - 120, 50, 90, WIDTH, HEIGHT)
        enemies = [Enemy(WIDTH), Enemy(WIDTH)]
        enemies[1].rect.y = -350
        coin = Coin(WIDTH)

        score = 0
        coin_score = 0
        enemy_speed = 5
        line_offset = 0
        game_over = False

        return player, enemies, coin, score, coin_score, enemy_speed, line_offset, game_over

    player, enemies, coin, score, coin_score, enemy_speed, line_offset, game_over = create_game()

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player, enemies, coin, score, coin_score, enemy_speed, line_offset, game_over = create_game()
                elif event.key == pygame.K_q:
                    running = False

        if not game_over:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_q]:
                running = False

            player.move(keys)

            # Road animation speed follows enemy speed
            line_offset = (line_offset + enemy_speed) % 60
            draw_road(screen, line_offset)

            # Update enemies
            for enemy in enemies:
                if enemy.update(enemy_speed):
                    enemy.reset()
                    score += 1

                enemy.draw(screen)

                # Collision with enemy = game over
                if player.rect.colliderect(enemy.rect):
                    game_over = True

            # Update coin
            coin.speed = enemy_speed
            if coin.update():
                coin.reset()

            # Collect coin
            if player.rect.colliderect(coin.rect):
                coin_score += coin.weight
                coin.reset()

            coin.draw(screen)

            enemy_speed = 5 + (coin_score // COINS_TO_INCREASE_SPEED)

            player.draw(screen)

            # Show score
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (20, 20))

            # Show collected coin value
            coin_text = font.render(f"Coins: {coin_score}", True, (255, 255, 0))
            coin_rect = coin_text.get_rect(topright=(WIDTH - 20, 20))
            screen.blit(coin_text, coin_rect)

            # Show enemy speed
            speed_text = font.render(f"Speed: {enemy_speed}", True, (255, 255, 255))
            screen.blit(speed_text, (20, 50))

        else:
            game_over_screen(screen, font_big, font_small, score, coin_score)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()