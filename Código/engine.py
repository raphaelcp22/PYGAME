import os
import sys
import pygame
import math
import random
from pygame.math import Vector2
import pygame.gfxdraw

# Diretórios de recursos
AUDIO_DIR = 'Áudios'
IMAGE_DIR = 'Imagens'

# Constantes globais
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
CELL_SIZE = 10
COLS, ROWS = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE
COUNTDOWN_TIME = 3
ORIGINAL_MAX_SPEED = 8
LAPS_TO_WIN = 10
LAP_COOLDOWN = 1 # ms
FPS = 60

# Cores
GRASS_SHADES = [(34, 177, 76), (30, 150, 60), (40, 200, 80)]
TRACK_COLOR = (40, 40, 40)
CURB_COLORS = [(200, 0, 0), (255, 255, 255)]
CHECKER_RED = (192, 57, 43)
CHECKER_WHITE = (236, 240, 241)
BORDER_COLOR = (120, 120, 120)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)
ORANGE = (255, 165, 0)
GREEN = (46, 204, 113)
PURPLE = (155, 89, 182)

# Função utilitária para fontes

def load_font(name, size):
    try:
        return pygame.font.Font(os.path.join(IMAGE_DIR, name), size)
    except:
        return pygame.font.Font(None, size)

# Sistema de partículas
class ParticleSystem:
    '''Essa classe é responsável por gerenciar o sistema de partículas do jogo, contendo as funções que permitem adicionar, atualizar, e impor efeitos visuais ao jogo, ainda mais quando se trata da física por trás (fumaça, explosões, etc.)'''
    def __init__(self):
        ''' Inicializa a lista e o sistema de partículas para o jogo funcionar'''
        self.particles = []
    def add_particle(self, x, y, color, velocity=None, size=5, lifetime=60, gravity=0.1, fade=True):
        '''Adiciona uma partícula ao sistema, possuindo posição, cor, duração, velocidade, tamanho, gravidade e se deve desaparecer de forma gradual'''
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
        '''Função responsável por atualizar as partículas, removendo as que expiraram ou que diminuíram de tamanho, ou até para movê-las'''
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += particle['gravity']
            particle['size'] += particle['growth']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0 or particle['size'] <= 0:
                self.particles.remove(particle)
    def draw(self, surface, camera=None):
        '''Função que é responsável por renderizar as partículas que estão na tela (com suporte a transparência e efeitos de fade)'''
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

class Car(pygame.sprite.Sprite):
    '''Essa classe tem a responsabilidade de gerenciar o carro do jogador, contendo as funções que fazem a lógica de movimento, colisão, física, e a renderização do carro que está na tela. Além disso, ela também controla o estado do automóvel.'''
    def __init__(self, x, y, color, controls, player_num):
        '''Função que inicializa o carro, carregando a sua imagem, definindo a sua posição inicial, a velocidade, aceleração, ângulo, e diversos outros atributos essenciais para o funcionamento do carro'''
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
        self.mask = pygame.mask.from_surface(self.image)

    def load_car_image(self, player_num):
        """Carrega imagem do carro baseado no número do jogador"""
        if player_num == 1:
            car_image = pygame.image.load(os.path.join(IMAGE_DIR, 'scarlet.png')).convert_alpha()
        elif player_num == 2:
            car_image = pygame.image.load(os.path.join(IMAGE_DIR, 'navy.png')).convert_alpha()
        else:
            raise ValueError("Número de jogador inválido")
        car_image = pygame.transform.rotate(car_image, -90)
        w, h = car_image.get_size()
        car_image = pygame.transform.smoothscale(car_image, (w / 1.2, h / 1.2))
        return car_image

    def update(self, cars, tilemap, grass_map, sound_available, engine_sound, crash_sound, boost_sound, lap_sound, particle_system):
        # ajustes de velocidade
        if self.health <= 0:
            self.max_speed = self.original_max_speed * 0.35
        elif self.in_pitstop:
            self.max_speed = self.original_max_speed / 3
        else:
            self.max_speed = self.original_max_speed

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

        # --- DETECÇÃO DE LINHA DE CHEGADA (copiado de game.py) ---
        current = pygame.time.get_ticks()
        if tile == 4 and math.sin(math.radians(self.angle)) > 0.7:
            if not self.crossed_finish and current - self.last_lap_time >= LAP_COOLDOWN:
                self.laps += 1
                self.last_lap_time = current
                self.crossed_finish = True
                if sound_available:
                    lap_sound.play()
        elif tile != 4:
            self.crossed_finish = False

        # efeitos do pit-stop
        if tile == 5:
            self.health = 100           # cura total
            self.max_speed = self.original_max_speed / 3  # reduz para 1/3
            self.in_pitstop = True
        elif self.in_pitstop and tile != 5:
            self.max_speed = self.original_max_speed      # restaura valor original
            self.in_pitstop = False

        # Lógica fora da pista (dano se ficar muito tempo fora)
        if tile in (0, 3):
            self.off_track = True
            self.off_track_timer += 1
            self.velocity *= 0.95
            if self.off_track_timer > 60 and self.collision_cooldown == 0:
                self.health = max(0, self.health - 2)
                self.collision_cooldown = 10
                if sound_available and random.random() < 0.1:
                    crash_sound.play()
        else:
            self.off_track = False
            self.off_track_timer = 0

        # Atualiza last_position antes de mover
        self.last_position = self.pos.copy()

        # muro sólido
        if tile == 6:
            self.pos = self.last_position.copy()
            self.velocity = Vector2(-self.velocity.x * 0.5, -self.velocity.y * 0.5)
            if sound_available:
                crash_sound.play()
            self.health = max(0, self.health - 10)
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
            self.mask = pygame.mask.from_surface(self.image)
            return
        # borda que empurra
        if tile == 7:
            self.pos = self.last_position.copy()
            self.velocity *= -0.3
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
            self.mask = pygame.mask.from_surface(self.image)
            return

        # Não deixa o carro sair da tela
        half_w, half_h = self.rect.width // 2, self.rect.height // 2
        new_x = min(max(new_pos.x, half_w), SCREEN_WIDTH - half_w)
        new_y = min(max(new_pos.y, half_h), SCREEN_HEIGHT - half_h)
        self.pos = Vector2(new_x, new_y)

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
        if tile == 4 and math.sin(math.radians(self.angle)) > 0.7:
            if not self.crossed_finish and current - self.last_lap_time >= LAP_COOLDOWN:
                self.laps += 1
                self.last_lap_time = current
                self.crossed_finish = True
                # som de volta
                if sound_available:
                    lap_sound.play()
                # victory check
                if self.laps >= LAPS_TO_WIN:
                    # O controle de game_state e winner_num deve ser feito no main loop
                    pass
        elif tile != 4:
            self.crossed_finish = False

        # Atualiza sprite
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        self.mask = pygame.mask.from_surface(self.image)

    def draw_skid_marks(self, surface):
        '''Função responsável por desenhar as marcas de derrapagem que aparecem na pista, tendo como base a posição do carro e o drift que foi feito, adicionando elementos da física ao jogo'''
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

# Funções de desenho

def draw_track(surface, tilemap, grass_map, track_tiles, grass_tiles, curb_tile):
    '''Desenha a pista, grama, bordas e elementos especiais (linha de chegada, pit-stop) baseado no tilemap'''
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
            elif tile == 5:  # pit-stop
                pygame.draw.rect(surface, BLUE, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif tile == 6:  # muro
                stripe_tile = pygame.Surface((CELL_SIZE, CELL_SIZE))
                for i in range(CELL_SIZE):
                    color = (0, 0, 0) if (i // 2) % 2 == 0 else (255, 215, 0)
                    pygame.draw.line(stripe_tile, color, (i, 0), (i, CELL_SIZE - 1))
                surface.blit(stripe_tile, (x * CELL_SIZE, y * CELL_SIZE))
            elif tile == 7:  # borda
                pygame.draw.rect(surface, (180, 180, 180), (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_hud(surface, cars, font_small):
    '''Função que renderiza o HUD do game, mostrando informações essenciais do carro, como vida, estado do turbo, voltas e o velocímetro'''
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
        lap_text   = font_small.render(f"VOLTAS:{min(car.laps, LAPS_TO_WIN)}/{LAPS_TO_WIN}", True, BLACK)
        surface.blit(lap_text, (pos_x, 105))
        # Indicador de velocidade
        speed = int(car.velocity.length() * 20)
        speed_text = font_small.render(f"{speed}KMH", True, BLACK)
        surface.blit(speed_text, (pos_x, 145))

def draw_intro(surface):
    '''Função que renderiza a tela de introdução do jogo, mostrando a imagem de fundo e como inicializá-lo'''
    intro_img = pygame.image.load(os.path.join(IMAGE_DIR, "intro_screen.png")).convert()
    intro_img = pygame.transform.scale(intro_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.blit(intro_img, (0, 0))

def draw_countdown(surface, count, font_huge):
    '''Função que mostra a contagem regressiva antes da corrida começar, com os números grandes, e no fim, a mensagem "VAI!"'''
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

def generate_grass_tiles():
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
    return grass_tiles

def generate_track_tiles():
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
    return track_tiles

def generate_curb_tile():
    curb_tile = pygame.Surface((CELL_SIZE, CELL_SIZE))
    for i in range(CELL_SIZE):
        color = CURB_COLORS[(i // 5) % 2]
        pygame.draw.line(curb_tile, color, (i, 0), (i, CELL_SIZE-1))
    return curb_tile
