import pygame
import sys

pygame.init()

# Dimensões
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formula Insper")
clock = pygame.time.Clock()

# Classe do Jogador
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 20)
        self.speed = 5
        self.color = (255, 0, 0)  # Vermelho

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Instancia o jogador
player = Player(WIDTH // 2, HEIGHT // 2)

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys)

        screen.fill((30, 30, 30))  # Fundo escuro
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()