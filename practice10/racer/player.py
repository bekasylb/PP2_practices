import pygame


class Player:
    def __init__(self, x, y, width, height, screen_width, screen_height):
        
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 100, 255)
        self.speed = 7
        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self, keys):
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed

        
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

       
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height

    def draw(self, screen):
        
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)

        
        window_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, 20)
        pygame.draw.rect(screen, (220, 240, 255), window_rect, border_radius=5)

        
        pygame.draw.rect(screen, (30, 30, 30), (self.rect.x - 4, self.rect.y + 8, 8, 16), border_radius=3)
        pygame.draw.rect(screen, (30, 30, 30), (self.rect.right - 4, self.rect.y + 8, 8, 16), border_radius=3)
        pygame.draw.rect(screen, (30, 30, 30), (self.rect.x - 4, self.rect.bottom - 24, 8, 16), border_radius=3)
        pygame.draw.rect(screen, (30, 30, 30), (self.rect.right - 4, self.rect.bottom - 24, 8, 16), border_radius=3)
