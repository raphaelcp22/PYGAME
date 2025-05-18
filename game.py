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
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self, x, y, color, controls):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0          # 0° points to the right
        self.size = (40, 20)
        self.color = color
        self.acc = 0.4
        self.reverse_acc = 0.2  # Slower acceleration in reverse
        self.rot_speed = 3
        self.controls = controls  # [left, right, accelerate, reverse]
        self.collision_rect = pygame.Rect(0, 0, *self.size)
        self.collision_rect.center = self.pos
        self.collided = False
        self.collision_timer = 0
        self.secondary_color = YELLOW if color == RED else WHITE
        self.is_reversing = False

    def update(self, keys):
        if keys[self.controls[0]]:
            self.angle += self.rot_speed
        if keys[self.controls[1]]:
            self.angle -= self.rot_speed
            
        # Forward movement
        if keys[self.controls[2]]:
            direction = pygame.Vector2(math.cos(math.radians(-self.angle)),
                                     math.sin(math.radians(-self.angle)))
            self.vel += direction * self.acc
            self.is_reversing = False
            
        # Reverse movement
        if keys[self.controls[3]]:
            direction = pygame.Vector2(math.cos(math.radians(-self.angle)),
                                     math.sin(math.radians(-self.angle)))
            self.vel -= direction * self.reverse_acc
            self.is_reversing = True
        
        # Friction
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
        # Create a surface for the car with per-pixel alpha
        car_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        
        # Draw car body
        pygame.draw.rect(car_surface, self.color, (0, 0, self.size[0], self.size[1]), border_radius=3)
        
        # Draw cockpit/windshield
        pygame.draw.rect(car_surface, BLACK, (10, 5, 20, 10), border_radius=2)
        
        # Draw racing stripes
        pygame.draw.line(car_surface, self.secondary_color, (5, 2), (35, 2), 2)
        pygame.draw.line(car_surface, self.secondary_color, (5, 18), (35, 18), 2)
        
        # Draw wheels
        pygame.draw.ellipse(car_surface, BLACK, (2, 5, 8, 10))
        pygame.draw.ellipse(car_surface, BLACK, (30, 5, 8, 10))
        
        # Draw wheel hubs and reverse lights if reversing
        pygame.draw.ellipse(car_surface, self.secondary_color, (5, 8, 4, 4))
        pygame.draw.ellipse(car_surface, self.secondary_color, (33, 8, 4, 4))
        
        # Draw reverse lights (red when reversing)
        if self.is_reversing:
            pygame.draw.rect(car_surface, (255, 100, 100), (35, 8, 3, 4))
        
        # Rotate and draw car
        rotated_car = pygame.transform.rotate(car_surface, self.angle)
        surf.blit(rotated_car, rotated_car.get_rect(center=self.pos))

def check_collision(player1, player2):
    if player1.collision_rect.colliderect(player2.collision_rect) and not player1.collided and not player2.collided:
        player1.vel *= -0.5
        player2.vel *= -0.5
        
        direction = player1.pos - player2.pos
        if direction.length() > 0:
            direction = direction.normalize()
            player1.pos += direction * 5
            player2.pos -= direction * 5
        
        player1.collided = True
        player2.collided = True
        player1.collision_timer = 30
        player2.collision_timer = 30

def draw_grass():
    cell = 20
    for y in range(0, HEIGHT, cell):
        for x in range(0, WIDTH, cell):
            col = GREEN1 if (x//cell + y//cell) % 2 else GREEN2
            pygame.draw.rect(screen, col, (x, y, cell, cell))

def draw_ui():
    font = pygame.font.SysFont('Arial', 24)
    text1 = font.render(f"RED Car: {int(player1.vel.length() * 10)} km/h", True, WHITE)
    text2 = font.render(f"BLUE Car: {int(player2.vel.length() * 10)} km/h", True, WHITE)
    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 40))
    
    # Add controls hint
    controls_font = pygame.font.SysFont('Arial', 16)
    hint1 = controls_font.render("Player 1: WASD to move, S to reverse", True, WHITE)
    hint2 = controls_font.render("Player 2: Arrows to move, DOWN to reverse", True, WHITE)
    screen.blit(hint1, (10, HEIGHT - 40))
    screen.blit(hint2, (10, HEIGHT - 20))

# Create players with controls [left, right, accelerate, reverse]
player1 = Player(WIDTH/2 - 100, HEIGHT/2, RED, 
                [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s])
player2 = Player(WIDTH/2 + 100, HEIGHT/2, BLUE,
                [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])

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