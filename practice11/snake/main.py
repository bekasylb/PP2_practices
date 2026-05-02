import pygame
from snake import Snake
from food import Food

WIDTH = 600
HEIGHT = 600
BLOCK = 20


def build_wall_cells():
    wall_cells = set()

    # Border walls
    for x in range(0, WIDTH, BLOCK):
        wall_cells.add((x, 0))
        wall_cells.add((x, HEIGHT - BLOCK))

    for y in range(0, HEIGHT, BLOCK):
        wall_cells.add((0, y))
        wall_cells.add((WIDTH - BLOCK, y))

    return wall_cells


def draw_walls(screen, wall_cells):
    for x, y in wall_cells:
        pygame.draw.rect(screen, (70, 70, 70), (x, y, BLOCK, BLOCK))


def game_over_screen(screen, font_big, font_small, score):
    screen.fill((15, 15, 15))
    title = font_big.render("GAME OVER", True, (255, 90, 90))
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 255))
    info = font_small.render("Press R to restart or Q to quit", True, (220, 220, 220))

    screen.blit(title, title.get_rect(center=(WIDTH // 2, 220)))
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 300)))
    screen.blit(info, info.get_rect(center=(WIDTH // 2, 400)))


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Practice11 Snake")

    font = pygame.font.SysFont("Arial", 24)
    font_big = pygame.font.SysFont("Arial", 42, bold=True)
    font_small = pygame.font.SysFont("Arial", 28)

    wall_cells = build_wall_cells()

    def create_game():
        snake = Snake(200, 200, BLOCK)
        food = Food(BLOCK, WIDTH, HEIGHT, wall_cells)
        food.respawn(snake.body)

        score = 0
        speed = 8
        game_over = False

        return snake, food, score, speed, game_over

    snake, food, score, speed, game_over = create_game()

    move_event = pygame.USEREVENT + 1
    pygame.time.set_timer(move_event, 1000 // speed)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.set_direction("UP")
                elif event.key == pygame.K_DOWN:
                    snake.set_direction("DOWN")
                elif event.key == pygame.K_LEFT:
                    snake.set_direction("LEFT")
                elif event.key == pygame.K_RIGHT:
                    snake.set_direction("RIGHT")
                elif event.key == pygame.K_q:
                    running = False

            elif not game_over and event.type == move_event:
                snake.move()
                head = snake.get_head()

                if head in wall_cells:
                    game_over = True

                head_x, head_y = head
                if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
                    game_over = True

                if snake.collided_with_self():
                    game_over = True

                if head == food.position:
                    score += food.weight
                    snake.grow(food.weight)

                    speed = 8 + score // 5
                    pygame.time.set_timer(move_event, max(60, 1000 // speed))

                    food.respawn(snake.body)

                elif food.expired():
                    food.respawn(snake.body)

            elif game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    snake, food, score, speed, game_over = create_game()
                    pygame.time.set_timer(move_event, 1000 // speed)
                elif event.key == pygame.K_q:
                    running = False

        if not game_over:
            screen.fill((20, 20, 20))

            draw_walls(screen, wall_cells)
            food.draw(screen)
            snake.draw(screen)

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            weight_text = font.render(f"Food weight: {food.weight}", True, (255, 255, 0))

            remaining_ms = max(0, food.life_time - (pygame.time.get_ticks() - food.spawn_time))
            timer_text = font.render(f"Food time: {remaining_ms // 1000}", True, (255, 180, 180))

            screen.blit(score_text, (20, 15))
            screen.blit(weight_text, (140, 15))
            screen.blit(timer_text, (320, 15))

        else:
            game_over_screen(screen, font_big, font_small, score)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()