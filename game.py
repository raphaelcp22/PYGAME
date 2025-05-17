import pygame, sys, math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formula Insper – protótipo 01")
clock = pygame.time.Clock()

GRAY = (60, 60, 60)
GREEN1, GREEN2 = (34, 177, 76), (40, 200, 80)

class Player:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0          # 0° aponta para a direita
        self.size = (40, 20)
        self.color = color
        self.acc = 0.4
        self.rot_speed = 3

    def update(self, keys):
        if keys[pygame.K_a]:
            self.angle += self.rot_speed
        if keys[pygame.K_d]:
            self.angle -= self.rot_speed
        if keys[pygame.K_w]:
            direction = pygame.Vector2(math.cos(math.radians(-self.angle)),
                                       math.sin(math.radians(-self.angle)))
            self.vel += direction * self.acc
        # atrito
        self.vel *= 0.98
        self.pos += self.vel

    def draw(self, surf):
        rect = pygame.Rect(0, 0, *self.size)
        rect.center = self.pos
        car = pygame.Surface(self.size)
        car.fill(self.color)
        rotated = pygame.transform.rotate(car, self.angle)
        surf.blit(rotated, rotated.get_rect(center=self.pos))

def draw_grass():
    cell = 20
    for y in range(0, HEIGHT, cell):
        for x in range(0, WIDTH, cell):
            col = GREEN1 if (x//cell + y//cell) % 2 else GREEN2
            pygame.draw.rect(screen, col, (x, y, cell, cell))

player = Player(WIDTH/2, HEIGHT/2, (255, 0, 0))

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    player.update(keys)

    draw_grass()
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)