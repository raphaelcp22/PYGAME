import pygame
import sys

pygame.init()

# Dimensões
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formula Insper - Dia 1")
clock = pygame.time.Clock()

# Jogador (placeholder)
player = pygame.Rect(WIDTH//2, HEIGHT//2, 40, 20)
player_speed = 5

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Pega teclas pressionadas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        if keys[pygame.K_UP]:
            player.y -= player_speed
        if keys[pygame.K_DOWN]:
            player.y += player_speed

        # Desenha fundo e "carro"
        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, (255, 0, 0), player)
        
        # Atualiza tela
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()