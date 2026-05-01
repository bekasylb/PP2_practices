import pygame
import random
from persistence import add_leaderboard_entry

WIDTH = 500
HEIGHT = 800
ROAD_X = 70
ROAD_W = 360
LANE_COUNT = 4
LANE_W = ROAD_W // LANE_COUNT
FINISH_DISTANCE = 3000


class Player:
    def __init__(self, color_name):
        self.w = 46
        self.h = 88
        self.x = ROAD_X + LANE_W // 2 - self.w // 2
        self.y = HEIGHT - 130
        self.speed = 6
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.color_name = color_name
        self.color = self.get_color(color_name)
        self.shield = False

    def get_color(self, name):
        colors = {
            "blue": (60, 120, 255),
            "red": (240, 70, 70),
            "green": (70, 200, 90),
            "yellow": (240, 220, 60),
        }
        return colors.get(name, (60, 120, 255))

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        if self.rect.left < ROAD_X:
            self.rect.left = ROAD_X
        if self.rect.right > ROAD_X + ROAD_W:
            self.rect.right = ROAD_X + ROAD_W
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(
            screen,
            (220, 240, 255),
            (self.rect.x + 10, self.rect.y + 12, self.rect.width - 20, 20),
            border_radius=5
        )
        pygame.draw.rect(screen, (25, 25, 25), (self.rect.x - 4, self.rect.y + 10, 8, 18), border_radius=3)
        pygame.draw.rect(screen, (25, 25, 25), (self.rect.right - 4, self.rect.y + 10, 8, 18), border_radius=3)
        pygame.draw.rect(screen, (25, 25, 25), (self.rect.x - 4, self.rect.bottom - 28, 8, 18), border_radius=3)
        pygame.draw.rect(screen, (25, 25, 25), (self.rect.right - 4, self.rect.bottom - 28, 8, 18), border_radius=3)

        if self.shield:
            pygame.draw.ellipse(screen, (100, 220, 255), self.rect.inflate(18, 18), 3)


class TrafficCar:
    def __init__(self, speed):
        lane = random.randint(0, LANE_COUNT - 1)
        self.w = 46
        self.h = 88
        self.rect = pygame.Rect(
            ROAD_X + lane * LANE_W + (LANE_W - self.w) // 2,
            random.randint(-900, -120),
            self.w,
            self.h
        )
        self.color = random.choice([(220, 50, 50), (180, 80, 220), (255, 140, 50)])
        self.speed = speed

    def update(self, extra_speed):
        self.rect.y += self.speed + extra_speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 235, 235), (self.rect.x + 10, self.rect.y + 12, self.rect.w - 20, 20), border_radius=5)

    def off_screen(self):
        return self.rect.top > HEIGHT


class Coin:
    def __init__(self, scroll_speed, player_rect):
        self.scroll_speed = scroll_speed
        self.reset(player_rect)

    def reset(self, player_rect):
        coin_type = random.choice([
            {"value": 1, "color": (205, 127, 50)},
            {"value": 2, "color": (192, 192, 192)},
            {"value": 3, "color": (255, 215, 0)},
        ])
        self.value = coin_type["value"]
        self.color = coin_type["color"]
        self.radius = 10 + self.value * 2

        while True:
            lane = random.randint(0, LANE_COUNT - 1)
            x = ROAD_X + lane * LANE_W + LANE_W // 2
            y = random.randint(-700, -100)
            rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
            if not rect.colliderect(player_rect.inflate(0, 180)):
                self.x = x
                self.y = y
                self.rect = rect
                break

    def update(self, speed):
        self.y += speed
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 245, 180), (self.x, self.y), max(2, self.radius - 4))

    def off_screen(self):
        return self.y - self.radius > HEIGHT


class Hazard:
    def __init__(self, kind, player_rect):
        self.kind = kind
        self.spawn(player_rect)

    def spawn(self, player_rect):
        while True:
            lane = random.randint(0, LANE_COUNT - 1)
            x = ROAD_X + lane * LANE_W + 8
            y = random.randint(-1000, -120)
            w = LANE_W - 16
            h = 26 if self.kind == "oil" else 34

            self.rect = pygame.Rect(x, y, w, h)

            if not self.rect.colliderect(player_rect.inflate(0, 180)):
                break

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        if self.kind == "oil":
            pygame.draw.ellipse(screen, (30, 30, 30), self.rect)
        elif self.kind == "slow":
            pygame.draw.rect(screen, (255, 170, 70), self.rect, border_radius=8)
            pygame.draw.line(screen, (120, 60, 0), self.rect.topleft, self.rect.bottomright, 3)
            pygame.draw.line(screen, (120, 60, 0), self.rect.topright, self.rect.bottomleft, 3)
        elif self.kind == "pothole":
            pygame.draw.ellipse(screen, (70, 70, 70), self.rect)
            pygame.draw.ellipse(screen, (30, 30, 30), self.rect.inflate(-8, -8))

    def off_screen(self):
        return self.rect.top > HEIGHT


class RoadEvent:
    def __init__(self, event_type, player_rect):
        self.event_type = event_type
        self.timer = 240
        self.active = True

        if event_type == "barrier":
            lane = random.randint(0, LANE_COUNT - 1)
            self.rect = pygame.Rect(
                ROAD_X + lane * LANE_W + 5,
                -80,
                LANE_W - 10,
                24
            )
            self.move_dir = random.choice([-1, 1])

        elif event_type == "nitro_strip":
            lane = random.randint(0, LANE_COUNT - 1)
            self.rect = pygame.Rect(
                ROAD_X + lane * LANE_W + 5,
                -120,
                LANE_W - 10,
                90
            )
            self.move_dir = 0

        else:  # speed_bump
            lane = random.randint(0, LANE_COUNT - 1)
            self.rect = pygame.Rect(
                ROAD_X + lane * LANE_W + 5,
                -80,
                LANE_W - 10,
                18
            )
            self.move_dir = 0

        if self.rect.colliderect(player_rect.inflate(0, 180)):
            self.rect.y -= 250

    def update(self, scroll_speed):
        self.rect.y += scroll_speed

        if self.event_type == "barrier":
            self.rect.x += self.move_dir * 2
            if self.rect.left < ROAD_X or self.rect.right > ROAD_X + ROAD_W:
                self.move_dir *= -1

        self.timer -= 1
        if self.timer <= 0 or self.rect.top > HEIGHT:
            self.active = False

    def draw(self, screen):
        if self.event_type == "barrier":
            pygame.draw.rect(screen, (220, 220, 220), self.rect, border_radius=6)
            pygame.draw.line(screen, (255, 60, 60), self.rect.topleft, self.rect.bottomright, 4)
            pygame.draw.line(screen, (255, 60, 60), self.rect.topright, self.rect.bottomleft, 4)

        elif self.event_type == "nitro_strip":
            pygame.draw.rect(screen, (50, 180, 255), self.rect, border_radius=6)
            for y in range(self.rect.top, self.rect.bottom, 14):
                pygame.draw.line(screen, (220, 245, 255), (self.rect.left + 8, y), (self.rect.right - 8, y), 3)

        elif self.event_type == "speed_bump":
            pygame.draw.rect(screen, (255, 200, 50), self.rect, border_radius=4)
            pygame.draw.line(screen, (100, 60, 0), self.rect.topleft, self.rect.bottomright, 3)


class PowerUp:
    def __init__(self, player_rect):
        self.reset(player_rect)

    def reset(self, player_rect):
        types = ["nitro", "shield", "repair"]
        self.kind = random.choice(types)
        self.timeout = 420
        self.radius = 14

        self.colors = {
            "nitro": (80, 180, 255),
            "shield": (100, 255, 180),
            "repair": (255, 120, 120),
        }

        while True:
            lane = random.randint(0, LANE_COUNT - 1)
            self.x = ROAD_X + lane * LANE_W + LANE_W // 2
            self.y = random.randint(-1200, -200)
            self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
            if not self.rect.colliderect(player_rect.inflate(0, 180)):
                break

    def update(self, speed):
        self.y += speed
        self.rect.center = (self.x, self.y)
        self.timeout -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.colors[self.kind], (self.x, self.y), self.radius)
        label = {
            "nitro": "N",
            "shield": "S",
            "repair": "R"
        }[self.kind]

        font = pygame.font.SysFont("Arial", 18, bold=True)
        text = font.render(label, True, (10, 10, 10))
        rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, rect)

    def expired(self):
        return self.timeout <= 0 or self.y - self.radius > HEIGHT


class RacerGame:
    def __init__(self, screen, clock, settings, player_name):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.player_name = player_name

        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 36, bold=True)

        self.player = Player(settings["car_color"])

        self.base_scroll_speed = {
            "easy": 5,
            "medium": 7,
            "hard": 9
        }[settings["difficulty"]]

        self.scroll_speed = self.base_scroll_speed
        self.traffic_speed_bonus = 0

        self.traffic = [TrafficCar(random.randint(3, 5)) for _ in range(3)]
        self.hazards = []
        self.road_events = []
        self.coins = [Coin(self.scroll_speed, self.player.rect) for _ in range(2)]
        self.powerup = PowerUp(self.player.rect)

        self.distance = 0
        self.coins_collected = 0
        self.score = 0

        self.active_powerup = None
        self.active_powerup_timer = 0
        self.repair_charges = 0

        self.dash_offset = 0
        self.running = True

    def draw_road(self):
        self.screen.fill((70, 170, 70))
        pygame.draw.rect(self.screen, (60, 60, 60), (ROAD_X, 0, ROAD_W, HEIGHT))

        for i in range(1, LANE_COUNT):
            x = ROAD_X + i * LANE_W
            pygame.draw.line(self.screen, (180, 180, 180), (x, 0), (x, HEIGHT), 2)

        pygame.draw.line(self.screen, (255, 255, 255), (ROAD_X, 0), (ROAD_X, HEIGHT), 4)
        pygame.draw.line(self.screen, (255, 255, 255), (ROAD_X + ROAD_W, 0), (ROAD_X + ROAD_W, HEIGHT), 4)

        dash_h = 36
        gap = 20
        self.dash_offset = (self.dash_offset + self.scroll_speed) % (dash_h + gap)
        y = -self.dash_offset

        middle_x = ROAD_X + ROAD_W // 2 - 4
        while y < HEIGHT:
            pygame.draw.rect(self.screen, (255, 255, 255), (middle_x, y, 8, dash_h))
            y += dash_h + gap

    def spawn_logic(self):
        density_bonus = self.distance // 600

        if len(self.traffic) < min(7, 3 + density_bonus) and random.random() < 0.015 + density_bonus * 0.002:
            self.traffic.append(TrafficCar(random.randint(3, 6)))

        if len(self.hazards) < min(6, 2 + density_bonus) and random.random() < 0.012 + density_bonus * 0.002:
            kind = random.choice(["oil", "slow", "pothole"])
            self.hazards.append(Hazard(kind, self.player.rect))

        if len(self.road_events) < 2 and random.random() < 0.004:
            event_type = random.choice(["barrier", "speed_bump", "nitro_strip"])
            self.road_events.append(RoadEvent(event_type, self.player.rect))

        if self.powerup.expired():
            self.powerup.reset(self.player.rect)

    def apply_difficulty_scaling(self):
        self.traffic_speed_bonus = self.distance // 800
        self.scroll_speed = self.base_scroll_speed + self.traffic_speed_bonus

        if self.active_powerup == "nitro":
            self.scroll_speed += 4

    def activate_powerup(self, kind):
        self.active_powerup = kind

        if kind == "nitro":
            self.active_powerup_timer = 240
        elif kind == "shield":
            self.player.shield = True
            self.active_powerup_timer = 0
        elif kind == "repair":
            self.repair_charges = 1
            self.active_powerup_timer = 0

    def resolve_collision(self):
        if self.player.shield:
            self.player.shield = False
            self.active_powerup = None
            return False

        if self.repair_charges > 0:
            self.repair_charges -= 1
            self.active_powerup = None
            return False

        return True

    def update_powerup_state(self):
        if self.active_powerup == "nitro":
            self.active_powerup_timer -= 1
            if self.active_powerup_timer <= 0:
                self.active_powerup = None

        elif self.active_powerup == "shield":
            if not self.player.shield:
                self.active_powerup = None

        elif self.active_powerup == "repair":
            if self.repair_charges <= 0:
                self.active_powerup = None

    def draw_hud(self):
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, WIDTH, 60))

        self.screen.blit(self.font.render(f"Player: {self.player_name}", True, (255, 255, 255)), (10, 8))
        self.screen.blit(self.font.render(f"Score: {self.score}", True, (255, 255, 255)), (10, 32))
        self.screen.blit(self.font.render(f"Coins: {self.coins_collected}", True, (255, 235, 80)), (170, 8))
        self.screen.blit(self.font.render(f"Distance: {self.distance}", True, (220, 220, 220)), (170, 32))

        remaining = max(0, FINISH_DISTANCE - self.distance)
        self.screen.blit(self.font.render(f"Finish in: {remaining}", True, (180, 255, 180)), (340, 8))

        if self.active_powerup == "nitro":
            msg = f"Power: Nitro ({self.active_powerup_timer // 60 + 1}s)"
        elif self.active_powerup == "shield":
            msg = "Power: Shield"
        elif self.active_powerup == "repair":
            msg = "Power: Repair"
        else:
            msg = "Power: None"

        self.screen.blit(self.small_font.render(msg, True, (255, 255, 255)), (340, 34))

    def compute_score(self):
        power_bonus = 30 if self.active_powerup else 0
        self.score = self.coins_collected * 15 + self.distance + power_bonus

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                return "quit"

            self.apply_difficulty_scaling()
            self.update_powerup_state()
            self.spawn_logic()

            self.player.update(keys)

            self.draw_road()

            # Distance
            self.distance += self.scroll_speed // 2

            # Traffic
            for car in self.traffic[:]:
                car.update(self.scroll_speed)
                car.draw(self.screen)

                if self.player.rect.colliderect(car.rect):
                    if self.resolve_collision():
                        self.compute_score()
                        add_leaderboard_entry(self.player_name, self.score, self.distance)
                        return {
                            "score": self.score,
                            "distance": self.distance,
                            "coins": self.coins_collected
                        }
                    else:
                        self.traffic.remove(car)
                        continue

                if car.off_screen():
                    self.traffic.remove(car)

            # Hazards
            slowed_this_frame = False
            for hazard in self.hazards[:]:
                hazard.update(self.scroll_speed)
                hazard.draw(self.screen)

                if self.player.rect.colliderect(hazard.rect):
                    if hazard.kind == "oil":
                        self.player.rect.x += random.choice([-5, 5])
                    elif hazard.kind == "slow":
                        slowed_this_frame = True
                    elif hazard.kind == "pothole":
                        if self.resolve_collision():
                            self.compute_score()
                            add_leaderboard_entry(self.player_name, self.score, self.distance)
                            return {
                                "score": self.score,
                                "distance": self.distance,
                                "coins": self.coins_collected
                            }
                        else:
                            self.hazards.remove(hazard)
                            continue

                if hazard.off_screen():
                    self.hazards.remove(hazard)

            if slowed_this_frame:
                self.scroll_speed = max(3, self.scroll_speed - 2)

            # Road events
            for road_event in self.road_events[:]:
                road_event.update(self.scroll_speed)
                road_event.draw(self.screen)

                if self.player.rect.colliderect(road_event.rect):
                    if road_event.event_type == "barrier":
                        if self.resolve_collision():
                            self.compute_score()
                            add_leaderboard_entry(self.player_name, self.score, self.distance)
                            return {
                                "score": self.score,
                                "distance": self.distance,
                                "coins": self.coins_collected
                            }
                        else:
                            road_event.active = False

                    elif road_event.event_type == "speed_bump":
                        self.scroll_speed = max(3, self.scroll_speed - 2)

                    elif road_event.event_type == "nitro_strip":
                        self.active_powerup = "nitro"
                        self.active_powerup_timer = 240
                        road_event.active = False

                if not road_event.active:
                    self.road_events.remove(road_event)

            # Coins
            for coin in self.coins:
                coin.update(self.scroll_speed)
                coin.draw(self.screen)

                if self.player.rect.colliderect(coin.rect):
                    self.coins_collected += coin.value
                    coin.reset(self.player.rect)

                elif coin.off_screen():
                    coin.reset(self.player.rect)

            # Power-up
            self.powerup.update(self.scroll_speed)
            self.powerup.draw(self.screen)

            if self.player.rect.colliderect(self.powerup.rect):
                self.activate_powerup(self.powerup.kind)
                self.powerup.reset(self.player.rect)

            self.player.draw(self.screen)
            self.compute_score()
            self.draw_hud()

            if self.distance >= FINISH_DISTANCE:
                add_leaderboard_entry(self.player_name, self.score + 200, self.distance)
                return {
                    "score": self.score + 200,
                    "distance": self.distance,
                    "coins": self.coins_collected
                }

            pygame.display.flip()

        return "quit"