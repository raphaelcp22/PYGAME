import pygame
import sys
import math
import random
from pygame.math import Vector2

# incicia o pygame
pygame.init()

# dimensões da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Racer Championship")
clock = pygame.time.Clock()


CELL_SIZE = 10
COLS, ROWS = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE

# cores
GRASS_SHADES = [(34, 177, 76), (30, 150, 60), (40, 200, 80)]
TRACK_COLOR = (40, 40, 40)
CURB_COLORS = [(200, 0, 0), (255, 255, 255)]
CHECKER_RED = (192, 57, 43)
CHECKER_WHITE = (236, 240, 241)
BORDER_COLOR = (120, 120, 120)

# geração de tiles de grama
grass_tiles = []
for shade in GRASS_SHADES:
    for _ in range(3):
        tile = pygame.Surface((CELL_SIZE, CELL_SIZE))
        tile.fill(shade)
        for _ in range(int(CELL_SIZE*CELL_SIZE*0.1)):
            rx = random.randrange(CELL_SIZE)
            ry = random.randrange(CELL_SIZE)
            tile.set_at((rx, ry), random.choice(GRASS_SHADES))
        grass_tiles.append(tile)

# tiles de pista
track_tiles = []
for _ in range(2):
    tile = pygame.Surface((CELL_SIZE, CELL_SIZE))
    tile.fill(TRACK_COLOR)
    for _ in range(int(CELL_SIZE*CELL_SIZE*0.02)):
        rx = random.randrange(CELL_SIZE)
        ry = random.randrange(CELL_SIZE)
        delta = random.choice([-5, 5])
        gray = max(0, min(255, TRACK_COLOR[0] + delta))
        tile.set_at((rx, ry), (gray, gray, gray))
    track_tiles.append(tile)

# tiles de borda (NÃO TESTADO AINDA - FAZER PISTA COM BORDAS)
curb_tile = pygame.Surface((CELL_SIZE, CELL_SIZE))
for i in range(CELL_SIZE):
    color = CURB_COLORS[(i // 5) % 2]
    pygame.draw.line(curb_tile, color, (i, 0), (i, CELL_SIZE-1))

# esvazia tilemap

CELL_SIZE = 10
COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE

tilemap = [[0 for _ in range(COLS)] for _ in range(ROWS)]
grass_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# carrega foto da pista
track_mask = pygame.image.load("track_mask.png").convert()
track_mask = pygame.transform.scale(track_mask, (COLS, ROWS))

for y in range(ROWS):
    for x in range(COLS):
        color = track_mask.get_at((x, y))[:3]
        if color == (40, 40, 40):        # pista
            tilemap[y][x] = 1
        elif color == (34, 177, 76):     # grama
            tilemap[y][x] = 0
        elif color == (255, 0, 0):   # borda
            tilemap[y][x] = 2
        elif color == (0, 0, 255):       # linha de chegada
            tilemap[y][x] = 4
        else:
            tilemap[y][x] = 0  # outros pixels são considerados grama

        # cria padrão de grama
        if tilemap[y][x] == 0 or tilemap[y][x] == 2:
            grass_map[y][x] = random.randrange(len(grass_tiles))

# outras cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)
ORANGE = (255, 165, 0)
GREEN = (46, 204, 113)
PURPLE = (155, 89, 182)

# fontes
try:
    font_large = pygame.font.Font('PressStart2P-Regular.ttf', 40)
    font_medium = pygame.font.Font('PressStart2P-Regular.ttf', 30)
    font_small = pygame.font.Font('PressStart2P-Regular.ttf', 20)
    font_tiny = pygame.font.Font('PressStart2P-Regular.ttf', 15)
    font_huge = pygame.font.Font('PressStart2P-Regular.ttf', 60)
except:
    font_large = pygame.font.Font(None, 80)
    font_medium = pygame.font.Font(None, 60)
    font_small = pygame.font.Font(None, 40)
    font_tiny = pygame.font.Font(None, 30)
    font_huge = pygame.font.Font(None, 100)

# centro da pista
TRACK_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, player_num):
        super().__init__()
        try:
            self.original_image = self.load_car_image(player_num)
        except pygame.error as e:
            print(f"Error loading car image for player {player_num}: {e}")
            sys.exit(1)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.angle = 0  # para direita
        self.acceleration = 0.3
        self.max_speed = 8
        self.reverse_speed = self.max_speed * 0.5
        self.friction = 0.05
        self.rotation_speed = 2.5
        self.drift_factor = 0.95
        self.traction = 1.0
        self.controls = controls
        self.player_num = player_num
        self.last_position = Vector2(x, y)
        self.off_track = False
        self.off_track_timer = 0

    def load_car_image(self, player_num):
        """Load car image based on player number."""
        if player_num == 1:
            car_image = pygame.image.load('scarlet.png').convert_alpha()
        elif player_num == 2:
            car_image = pygame.image.load('navy.png').convert_alpha()
        else:
            raise ValueError("Invalid player number")
        return pygame.transform.rotate(car_image, -90)
    
    def update(self, cars):
        keys = pygame.key.get_pressed()
        
        # controles
        if keys[self.controls['accelerate']]:
            self.velocity += Vector2(math.cos(math.radians(self.angle)), 
                                   math.sin(math.radians(self.angle))) * self.acceleration
        
        if keys[self.controls['brake']]:
            self.velocity -= Vector2(math.cos(math.radians(self.angle)), 
                                   math.sin(math.radians(self.angle))) * (self.acceleration * 0.8)
        
        # direção
        turning = 0
        if keys[self.controls['left']]:
            turning += self.rotation_speed * (1 - (0.7 * (self.velocity.length() / self.max_speed)))
        if keys[self.controls['right']]:
            turning -= self.rotation_speed * (1 - (0.7 * (self.velocity.length() / self.max_speed)))
        
        if self.velocity.length() > 0.5:
            self.angle += turning * (self.velocity.length() / self.max_speed)
        
        # fricção
        self.velocity *= (1 - self.friction * self.traction)
        
        # vel. máxima
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        
        # calcula nova posição
        new_pos = self.pos + self.velocity
        
        # sistema de colisão/detecção de pista
        cell_x = int(new_pos.x / CELL_SIZE)
        cell_y = int(new_pos.y / CELL_SIZE)

        if (0 <= cell_x < COLS and 0 <= cell_y < ROWS and 
            tilemap[cell_y][cell_x] in (0, 3)):  # fora da pista
            self.off_track = True
            self.off_track_timer += 1
            self.velocity *= 0.95
        else:
            self.off_track = False
            self.off_track_timer = 0

        self.pos = new_pos
        
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
    
    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle)
        rect = rotated_image.get_rect(center=(self.pos.x, self.pos.y))
        surface.blit(rotated_image, rect)

def draw_track(surface):
    for y in range(ROWS):
        for x in range(COLS):
            tile = tilemap[y][x]
            if tile == 1:
                surface.blit(random.choice(track_tiles), (x*CELL_SIZE, y*CELL_SIZE))
            elif tile == 0:
                surface.blit(grass_tiles[grass_map[y][x]], (x*CELL_SIZE, y*CELL_SIZE))
            elif tile == 2:
                surface.blit(curb_tile, (x*CELL_SIZE, y*CELL_SIZE))
            elif tile == 4:
                pygame.draw.rect(surface, (0, 0, 255), (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_hud(surface, cars):
    for i, car in enumerate(cars):

        player_text = font_small.render(f"P{car.player_num}", True, WHITE)
        pos_x = 20 if i == 0 else SCREEN_WIDTH - 120
        surface.blit(player_text, (pos_x, 20))
        
        # indicador de velocidade
        speed = int(car.velocity.length() * 20)
        speed_text = font_small.render(f"{speed}KMH", True, WHITE)
        surface.blit(speed_text, (pos_x, 60))

def draw_intro(surface):
    # intro screen
    intro_img = pygame.image.load("intro_screen.png").convert()
    intro_img = pygame.transform.scale(intro_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.blit(intro_img, (0, 0))

def draw_countdown(surface, count):

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))
    
    if count > 0:
        count_text = font_huge.render(str(count), True, WHITE)
        surface.blit(count_text, (SCREEN_WIDTH//2 - count_text.get_width()//2, 
                                 SCREEN_HEIGHT//2 - count_text.get_height()//2))
    else:
        go_text = font_huge.render("GO!", True, GREEN)
        surface.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, 
                              SCREEN_HEIGHT//2 - go_text.get_height()//2))

def main():
    game_state = "intro"
    countdown = 3
    last_tick = pygame.time.get_ticks()
    cars = []
    
    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game_state == "intro" and event.key == pygame.K_SPACE:
                    controls1 = {
                        'accelerate': pygame.K_w,
                        'brake': pygame.K_s,
                        'left': pygame.K_d,
                        'right': pygame.K_a
                    }
                    controls2 = {
                        'accelerate': pygame.K_UP,
                        'brake': pygame.K_DOWN,
                        'left': pygame.K_RIGHT,
                        'right': pygame.K_LEFT
                    }
                    start_y = 160  # ajustar para a pista
                    car1 = Car(TRACK_CENTER[0] - 60, start_y, RED, controls1, 1)
                    car2 = Car(TRACK_CENTER[0] + 60, start_y, BLUE, controls2, 2)
                    cars = [car1, car2]
                    game_state = "countdown"
                    last_tick = current_time
                    countdown = 3
                
                elif game_state == "racing":
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
        
        if game_state == "countdown":
            if current_time - last_tick >= 1000:
                countdown -= 1
                last_tick = current_time
                if countdown < 0:
                    game_state = "racing"
        
        elif game_state == "racing":
            for car in cars:
                car.update(cars)
        
        screen.fill(BLACK)
        
        if game_state == "intro":
            draw_intro(screen)
        else:
            draw_track(screen)
            
            if game_state in ["countdown", "racing"]:
                for car in cars:
                    car.draw(screen)
                    
            if game_state in ["countdown", "racing"] and cars:
                draw_hud(screen, cars)
            
            if game_state == "countdown":
                draw_countdown(screen, countdown)

                
            controls_text = font_tiny.render("WASD/ARROWS TO MOVE", True, WHITE)
            screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()