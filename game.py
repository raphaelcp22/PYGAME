import pygame
import sys
import math
import random
from pygame.math import Vector2
import pygame.gfxdraw  # Partículas em pixel art

# features faltando:
# contagem de voltas com detecção de linha de chegada
# tiles de muro ou areia para evitar trapaça

# inicia o pygame
pygame.init()

# inicia o sistema de som
pygame.mixer.init()

# Ajustes de tela e constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
CELL_SIZE = 10
COLS, ROWS = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE
TRACK_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
COUNTDOWN_TIME = 3
REQUIRED_LAPS = 5
ORIGINAL_MAX_SPEED = 8  # pit-stop: valor original da velocidade máxima

# constantes do sistema de voltas
LAPS_TO_WIN = 10
LAP_COOLDOWN = 100  # ms

game_state = "intro"
winner_num = None

# dimensões da tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Racer Championship")
clock = pygame.time.Clock()

# carrega sons
try:
    engine_sound = pygame.mixer.Sound('engine.mp3')  # som do motor
    crash_sound = pygame.mixer.Sound('crash.mp3')    # som de colisão
    boost_sound = pygame.mixer.Sound('boost.mp3')    # som de turbo
    lap_sound = pygame.mixer.Sound('lap.mp3')        # som de volta
    music = pygame.mixer.music.load('race_music.mp3')  # música de fundo
    pygame.mixer.music.set_volume(0.5)  # volume mais baixo pra música
    sound_available = True
except:
    sound_available = False
    print("Arquivos de som não encontrados. Continuando sem som.")


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

# tiles de borda
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
track_mask = pygame.image.load("track_mask3.png").convert()
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
        elif color == (255, 255, 255):   # detecção de pit-stop
            tilemap[y][x] = 5
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

# Sistema de partículas
class ParticleSystem:
    def __init__(self):
        self.particles = []
    def add_particle(self, x, y, color, velocity=None, size=5, lifetime=60, gravity=0.1, fade=True):
        if velocity is None:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        self.particles.append({
            'x': x, 'y': y, 'color': color, 'vx': velocity[0], 'vy': velocity[1],
            'size': size, 'max_size': size, 'lifetime': lifetime, 'max_lifetime': lifetime,
            'gravity': gravity, 'fade': fade, 'growth': random.uniform(-0.1, 0.3)
        })
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += particle['gravity']
            particle['size'] += particle['growth']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0 or particle['size'] <= 0:
                self.particles.remove(particle)
    def draw(self, surface, camera=None):
        for particle in self.particles:
            alpha = 255
            if particle['fade']:
                alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            size = max(1, particle['size'])
            color = list(particle['color'])
            if len(color) == 3:
                color.append(alpha)
            else:
                color[3] = alpha
            pos = (int(particle['x']), int(particle['y']))
            if camera:
                pos = (int(particle['x'] + camera.camera.x), int(particle['y'] + camera.camera.y))
            if size > 2:
                pygame.gfxdraw.filled_circle(surface, pos[0], pos[1], int(size), color)
                pygame.gfxdraw.aacircle(surface, pos[0], pos[1], int(size), color)
            else:
                pygame.draw.circle(surface, color, pos, int(size))

particle_system = ParticleSystem()

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, player_num):
        super().__init__()
        try:
            self.original_image = self.load_car_image(player_num)
        except pygame.error as e:
            print(f"Erro ao carregar imagem do carro para o jogador {player_num}: {e}")
            sys.exit(1)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.angle = 0
        self.acceleration = 0.26
        self.max_speed = ORIGINAL_MAX_SPEED
        self.original_max_speed = ORIGINAL_MAX_SPEED  # pit-stop: para restaurar
        self.reverse_speed = self.max_speed * 0.5
        self.friction = 0.05
        self.rotation_speed = 5
        self.drift_factor = 2
        self.traction = 1.0
        self.controls = controls
        self.player_num = player_num
        self.last_position = Vector2(x, y)
        self.skid_marks = []
        self.boost = 100
        self.boosting = False
        self.boost_power = 1.5
        self.drifting = False
        self.health = 100
        self.invincible = 0
        self.visible = True
        self.flash_timer = 0
        self.engine_sound_playing = False
        self.collision_cooldown = 0
        self.last_collision_time = 0
        self.drift_angle = 0
        self.speed_effect_timer = 0
        self.off_track = False
        self.off_track_timer = 0
        # variaveis das voltas
        self.laps = 0
        self.last_lap_time = -LAP_COOLDOWN
        self.crossed_finish = False
        self.in_pitstop = False  # pit-stop: flag para saber se está no pit

    def load_car_image(self, player_num):
        """Carrega imagem do carro baseado no número do jogador"""
        if player_num == 1:
            car_image = pygame.image.load('scarlet.png').convert_alpha()
        elif player_num == 2:
            car_image = pygame.image.load('navy.png').convert_alpha()
        else:
            raise ValueError("Número de jogador inválido")
        return pygame.transform.rotate(car_image, -90)
    
    def update(self, cars):
        # Verifica se o carro está sem vida e ajusta a velocidade
        if self.health <= 0:
            self.max_speed = self.original_max_speed * 0.5  # 50% da velocidade normal
        else:
            self.max_speed = self.original_max_speed  # velocidade normal

        keys = pygame.key.get_pressed()
        # Cooldowns
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1
        if self.invincible > 0:
            self.flash_timer += 1
            self.visible = self.flash_timer % 10 < 5
            self.invincible -= 1
        else:
            self.visible = True

        # Som do motor
        if sound_available:
            engine_volume = min(0.7, self.velocity.length() / self.max_speed)
            if engine_volume > 0.1:
                if not self.engine_sound_playing:
                    engine_sound.play(-1)
                    self.engine_sound_playing = True
                engine_sound.set_volume(engine_volume)
            else:
                if self.engine_sound_playing:
                    engine_sound.stop()
                    self.engine_sound_playing = False

        # Controles
        if keys[self.controls['accelerate']]:
            self.velocity += Vector2(math.cos(math.radians(self.angle)),
                                    math.sin(math.radians(self.angle))) * self.acceleration
        if keys[self.controls['brake']]:
            self.velocity -= Vector2(math.cos(math.radians(self.angle)),
                                    math.sin(math.radians(self.angle))) * (self.acceleration * 0.8)

        # Turbo
        self.boosting = False
        if keys[self.controls['boost']] and self.boost > 0 and self.velocity.length() > 0:
            boost_amount = self.acceleration * self.boost_power
            self.velocity += Vector2(math.cos(math.radians(self.angle)),
                                    math.sin(math.radians(self.angle))) * boost_amount
            self.boost -= 1.5
            self.boosting = True
            if sound_available and random.random() < 0.1:
                boost_sound.play()
            if random.random() < 0.2:
                particle_system.add_particle(
                    self.pos.x + math.cos(math.radians(self.angle + 180)) * 30,
                    self.pos.y + math.sin(math.radians(self.angle + 180)) * 30,
                    (255, 200, 100),
                    (0, -0.5),
                    10, 35, 0.05, False
                )
        if not self.boosting and self.boost < 100:
            self.boost += 0.2

        # Direção & drift
        turning = 0
        if keys[self.controls['left']]:
            turning += self.rotation_speed * (1 - (0.7 * (self.velocity.length() / self.max_speed)))
        if keys[self.controls['right']]:
            turning -= self.rotation_speed * (1 - (0.7 * (self.velocity.length() / self.max_speed)))
        if self.velocity.length() > 0.5:
            self.angle += turning * (self.velocity.length() / self.max_speed)

        # Lógica de drift
        self.drifting = False
        if self.velocity.length() > self.max_speed * 0.6 and abs(turning) > 0.5:
            self.drifting = True
            self.traction = 0.8
            self.drift_angle = turning * 0.5
            if random.random() < 0.3 and self.velocity.length() > 2:
                self.skid_marks.append({
                    'pos': Vector2(self.pos.x, self.pos.y),
                    'angle': self.angle,
                    'life': 100
                })
                particle_system.add_particle(
                    self.pos.x + math.cos(math.radians(self.angle + 90)) * 20,
                    self.pos.y + math.sin(math.radians(self.angle + 90)) * 20,
                    (80, 80, 80),
                    None, 4, 45, 0, True
                )
        else:
            self.traction = 1.0
            self.drift_angle *= 0.9
        if self.drifting:
            self.angle += self.drift_angle

        # Atrito
        self.velocity *= (1 - self.friction * self.traction)
        # Limite de velocidade
        if self.velocity.length() > self.max_speed * (1.5 if self.boosting else 1.0):
            self.velocity.scale_to_length(self.max_speed * (1.5 if self.boosting else 1.0))

        # Nova posição
        new_pos = self.pos + self.velocity
        cell_x = int(new_pos.x / CELL_SIZE)
        cell_y = int(new_pos.y / CELL_SIZE)
        tile = tilemap[cell_y][cell_x] if 0 <= cell_x < COLS and 0 <= cell_y < ROWS else 0

        # --- aplica efeitos do pit-stop ---
        if tile == 5:
            self.health = 100  # cura total
            self.max_speed = self.original_max_speed * 0.5 if self.health <= 0 else self.original_max_speed  # mantém 50% se sem vida
            self.in_pitstop = True
        elif self.in_pitstop and tile != 5:
            self.max_speed = self.original_max_speed * 0.5 if self.health <= 0 else self.original_max_speed  # mantém 50% se sem vida
            self.in_pitstop = False

        # Lógica fora da pista (dano se ficar muito tempo fora)
        if tile in (0, 3):
            self.off_track = True
            self.off_track_timer += 1
            self.velocity *= 0.95
            if self.off_track_timer > 60 and self.collision_cooldown == 0:
                self.health = max(0, self.health - 1)
                self.collision_cooldown = 10
                if sound_available and random.random() < 0.1:
                    crash_sound.play()
        else:
            self.off_track = False
            self.off_track_timer = 0

        self.pos = new_pos

        # Física de colisão entre carros
        current_time = pygame.time.get_ticks()
        for car in cars:
            if (car != self and pygame.sprite.collide_mask(self, car)
                and current_time - self.last_collision_time > 500):
                self.last_collision_time = current_time
                collision_angle = math.atan2(car.pos.y - self.pos.y, car.pos.x - self.pos.x)
                relative_velocity = self.velocity - car.velocity
                force = relative_velocity.length() * 0.7
                if force > 2:
                    damage = force * 2
                    if self.collision_cooldown == 0:
                        self.health = max(0, self.health - damage)
                        self.invincible = 15
                        self.collision_cooldown = 30
                    if car.collision_cooldown == 0:
                        car.health = max(0, car.health - damage)
                        car.invincible = 15
                        car.collision_cooldown = 30
                    if sound_available:
                        crash_sound.play()
                impulse = Vector2(math.cos(collision_angle), math.sin(collision_angle)) * force
                self.velocity -= impulse * 0.7
                car.velocity += impulse * 0.7
                for _ in range(int(force * 8)):
                    particle_system.add_particle(
                        (self.pos.x + car.pos.x) / 2,
                        (self.pos.y + car.pos.y) / 2,
                        (200, 200, 200),
                        (random.uniform(-force, force), random.uniform(-force, force)),
                        5, 35, 0.1, True
                    )

        # Efeito de linhas de velocidade
        if self.velocity.length() > self.max_speed * 0.8:
            self.speed_effect_timer += 1
            if self.speed_effect_timer % 3 == 0:
                for _ in range(2):
                    offset = random.uniform(-20, 20)
                    particle_system.add_particle(
                        self.pos.x + math.cos(math.radians(self.angle + 180 + offset)) * 40,
                        self.pos.y + math.sin(math.radians(self.angle + 180 + offset)) * 40,
                        (255, 255, 255, 150),
                        (random.uniform(-1, 1), random.uniform(-1, 1)),
                        3, 25, 0, True
                    )

        # detecção de voltas
        current = pygame.time.get_ticks()
        if tile == 4 and math.sin(math.radians(self.angle)) < -0.7:
            if not self.crossed_finish and current - self.last_lap_time >= LAP_COOLDOWN:
                self.laps += 1
                self.last_lap_time = current
                self.crossed_finish = True
                # som de volta
                if sound_available:
                    lap_sound.play()
                # victory check
                global game_state, winner_num
                if self.laps >= LAPS_TO_WIN:
                    game_state = "winner"
                    winner_num = self.player_num
        elif tile != 4:
            self.crossed_finish = False

        # Atualiza sprite
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def draw_skid_marks(self, surface):
        for skid in self.skid_marks[:]:
            skid['life'] -= 1
            if skid['life'] <= 0:
                self.skid_marks.remove(skid)
            else:
                alpha = int(255 * (skid['life'] / 100))
                skid_surface = pygame.Surface((25, 10), pygame.SRCALPHA)
                pygame.draw.rect(skid_surface, (80, 80, 80, alpha), (0, 0, 25, 10))
                rotated_skid = pygame.transform.rotate(skid_surface, -skid['angle'])
                surface.blit(rotated_skid, rotated_skid.get_rect(center=skid['pos']))

    def draw(self, surface):
        if self.visible:
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
                # padrão xadrez preto e branco para a linha de chegada
                checker_tile = pygame.Surface((CELL_SIZE, CELL_SIZE))
                if (x + y) % 2 == 0:  # alterna as cores em padrão xadrez
                    checker_tile.fill(WHITE)
                else:
                    checker_tile.fill(BLACK)
                surface.blit(checker_tile, (x*CELL_SIZE, y*CELL_SIZE))
            elif tile == 5:
                # renderização do pit-stop
                pygame.draw.rect(surface, BLUE, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_hud(surface, cars):
    for i, car in enumerate(cars):
        player_text = font_small.render(f"P{car.player_num}", True, WHITE)
        pos_x = 20 if i == 0 else SCREEN_WIDTH - 120
        surface.blit(player_text, (pos_x, 20))
        # Barra de vida (estilo pixel)
        health_width = int(100 * (car.health / 100))
        pygame.draw.rect(surface, (40, 40, 40), (pos_x, 60, 100, 15))
        pygame.draw.rect(surface, GREEN, (pos_x, 60, health_width, 15))
        for seg in range(0, health_width, 10):
            pygame.draw.rect(surface, (0, 100, 0), (pos_x + seg, 60, 8, 15))
        pygame.draw.rect(surface, WHITE, (pos_x, 60, 100, 15), 2)
        # Barra de turbo (estilo pixel)
        boost_width = int(100 * (car.boost / 100))
        pygame.draw.rect(surface, (20, 20, 20), (pos_x, 85, 100, 10))
        pygame.draw.rect(surface, YELLOW, (pos_x, 85, boost_width, 10))
        for seg in range(0, boost_width, 10):
            pygame.draw.rect(surface, (180, 180, 0), (pos_x + seg, 85, 8, 10))
        pygame.draw.rect(surface, WHITE, (pos_x, 85, 100, 10), 1)
        # Contador de voltas
        lap_text = font_small.render(f"VOLTAS:{min(car.laps, LAPS_TO_WIN)}/{LAPS_TO_WIN}", True, WHITE)
        surface.blit(lap_text, (pos_x, 105))
        # Indicador de velocidade
        speed = int(car.velocity.length() * 20)
        speed_text = font_small.render(f"{speed}KMH", True, WHITE)
        surface.blit(speed_text, (pos_x, 145))

def draw_intro(surface):
    # tela de introdução
    intro_img = pygame.image.load("intro_screen.png").convert()
    intro_img = pygame.transform.scale(intro_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.blit(intro_img, (0, 0))

def draw_countdown(surface, count):
    # contagem regressiva
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))
    
    if count > 0:
        count_text = font_huge.render(str(count), True, WHITE)
        surface.blit(count_text, (SCREEN_WIDTH//2 - count_text.get_width()//2, 
                                 SCREEN_HEIGHT//2 - count_text.get_height()//2))
    else:
        go_text = font_huge.render("VAI!", True, GREEN)
        surface.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, 
                              SCREEN_HEIGHT//2 - go_text.get_height()//2))

def main():
    global particle_system
    global game_state, winner_num
    # toca música de fundo se disponível
    if sound_available:
        pygame.mixer.music.play(-1)  # loop na música
    
    countdown = 3
    last_tick = pygame.time.get_ticks()
    cars = []

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # para todos os sons ao sair
                if sound_available:
                    pygame.mixer.music.stop()
                    engine_sound.stop()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game_state == "intro" and event.key == pygame.K_SPACE:
                    # controles do jogador 1 (WASD + Shift)
                    controls1 = {
                        'accelerate': pygame.K_w,
                        'brake': pygame.K_s,
                        'left': pygame.K_d,
                        'right': pygame.K_a,
                        'boost': pygame.K_LSHIFT
                    }
                    # controles do jogador 2 (setas + Ctrl)
                    controls2 = {
                        'accelerate': pygame.K_UP,
                        'brake': pygame.K_DOWN,
                        'left': pygame.K_RIGHT,
                        'right': pygame.K_LEFT,
                        'boost': pygame.K_RCTRL
                    }
                    start_y = 160  # posição inicial na pista
                    car1 = Car(TRACK_CENTER[0] - 60, start_y, RED, controls1, 1)
                    car2 = Car(TRACK_CENTER[0] + 60, start_y, BLUE, controls2, 2)
                    cars = [car1, car2]
                    game_state = "countdown"
                    last_tick = current_time
                    countdown = 3
                
                elif game_state == "racing":
                    if event.key == pygame.K_q:
                        if sound_available:
                            pygame.mixer.music.stop()
                            engine_sound.stop()
                        pygame.quit()
                        sys.exit()
                # controles da tela de vitória
                elif game_state == "winner":
                    if event.key == pygame.K_q:
                        if sound_available:
                            pygame.mixer.music.stop()
                            engine_sound.stop()
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        # restart game
                        game_state = "intro"
                        winner_num = None

        # lógica da contagem regressiva
        if game_state == "countdown":
            if current_time - last_tick >= 1000:
                countdown -= 1
                last_tick = current_time
                if countdown < 0:
                    game_state = "racing"
        
        # atualiza os carros durante a corrida
        elif game_state == "racing":
            for car in cars:
                car.update(cars)
        
        particle_system.update()
        # desenha tudo
        screen.fill(BLACK)
        
        # tela de vitória
        if game_state == "winner":
            # bloqueia desenhos normais, só mostra a imagem de vitória
            screen.fill(BLACK)
            img = pygame.image.load(f"player{winner_num}_win.png").convert_alpha()
            img = pygame.transform.scale(img, (400, 300))
            screen.blit(img, ((SCREEN_WIDTH - img.get_width()) // 2, (SCREEN_HEIGHT - img.get_height()) // 2))
        else:
            if game_state == "intro":
                draw_intro(screen)
            else:
                draw_track(screen)
                
                if game_state in ["countdown", "racing"]:
                    for car in cars:
                        car.draw(screen)
                        
                        # efeito visual do turbo
                        if car.boosting:
                            boost_pos = car.pos + Vector2(
                                math.cos(math.radians(car.angle + 180)) * 35,
                                math.sin(math.radians(car.angle + 180)) * 35
                            )
                            pygame.draw.circle(
                                screen, 
                                (255, 200, 100, 180), 
                                (int(boost_pos.x), int(boost_pos.y)), 
                                20
                            )
                
                # mostra HUD durante a corrida
                if game_state in ["countdown", "racing"] and cars:
                    draw_hud(screen, cars)
                
                # mostra contagem regressiva
                if game_state == "countdown":
                    draw_countdown(screen, countdown)
                
                # instruções de controle
                controls_text = font_tiny.render("WASD/SETA PARA MOVER, SHIFT/CTRL PARA TURBO", True, WHITE)
                screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 40))
        
        if game_state not in ["intro"]:
            for car in cars:
                car.draw_skid_marks(screen)
            particle_system.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()