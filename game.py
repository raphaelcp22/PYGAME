import pygame
import sys
import math
from pygame.math import Vector2

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formula Insper – 2 Player Racing")
clock = pygame.time.Clock()

GRAY = (60, 60, 60)
GREEN1, GREEN2 = (34, 177, 76), (40, 200, 80)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
WHITE = (255, 255, 255)

class Player:
    def __init__(self, x, y, color, controls):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0          # 0° aponta para a direita
        self.size = (40, 20)
        self.color = color
        self.acc = 0.4
        self.rot_speed = 3
        self.controls = controls  # [left, right, accelerate]
        self.collision_rect = pygame.Rect(0, 0, *self.size)
        self.collision_rect.center = self.pos
        self.collided = False
        self.collision_timer = 0

    def update(self, keys):
        if keys[self.controls[0]]:
            self.angle += self.rot_speed
        if keys[self.controls[1]]:
            self.angle -= self.rot_speed
        if keys[self.controls[2]]:
            direction = pygame.Vector2(math.cos(math.radians(-self.angle)),
                                     math.sin(math.radians(-self.angle)))
            self.vel += direction * self.acc
        
        # atrito
        self.vel *= 0.98
        self.pos += self.vel
        
        # Update collision rectangle
        self.collision_rect.center = self.pos
        
        # Screen boundaries
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))
        
        # Collision cooldown
        if self.collided:
            self.collision_timer -= 1
            if self.collision_timer <= 0:
                self.collided = False

    def draw(self, surf):
        rect = pygame.Rect(0, 0, *self.size)
        rect.center = self.pos
        car = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(car, self.color, rect)
        
        # Add some details to the car
        pygame.draw.rect(car, WHITE, (5, 5, 10, 10))
        pygame.draw.rect(car, WHITE, (25, 5, 10, 10))
        
        rotated = pygame.transform.rotate(car, self.angle)
        surf.blit(rotated, rotated.get_rect(center=self.pos))
        
        # Draw collision rectangle (for debugging)
        # pygame.draw.rect(surf, (255, 255, 0), self.collision_rect, 1)

def check_collision(player1, player2):
    # Simple rectangle collision detection
    if player1.collision_rect.colliderect(player2.collision_rect) and not player1.collided and not player2.collided:
        # Calculate collision response (simple bounce)
        player1.vel *= -0.5
        player2.vel *= -0.5
        
        # Move players apart slightly to prevent sticking
        direction = player1.pos - player2.pos
        if direction.length() > 0:
            direction = direction.normalize()
            player1.pos += direction * 5
            player2.pos -= direction * 5
        
        # Set collision state
        player1.collided = True
        player2.collided = True
        player1.collision_timer = 30  # 0.5 seconds at 60 FPS
        player2.collision_timer = 30

def draw_grass():
    cell = 20
    for y in range(0, HEIGHT, cell):
        for x in range(0, WIDTH, cell):
            col = GREEN1 if (x//cell + y//cell) % 2 else GREEN2
            pygame.draw.rect(screen, col, (x, y, cell, cell))

def draw_ui():
    font = pygame.font.SysFont(None, 36)
    text1 = font.render(f"Player 1 Speed: {int(player1.vel.length() * 10)}", True, WHITE)
    text2 = font.render(f"Player 2 Speed: {int(player2.vel.length() * 10)}", True, WHITE)
    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 50))

# Create two players with different controls
player1 = Player(WIDTH/2 - 100, HEIGHT/2, RED, [pygame.K_a, pygame.K_d, pygame.K_w])
player2 = Player(WIDTH/2 + 100, HEIGHT/2, BLUE, [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP])

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    player1.update(keys)
    player2.update(keys)
    
    check_collision(player1, player2)

    draw_grass()
    player1.draw(screen)
    player2.draw(screen)
    draw_ui()

    pygame.display.flip()
    clock.tick(60)