from engine import *
from engine import generate_grass_tiles, generate_track_tiles, generate_curb_tile, draw_track, draw_hud, draw_intro, draw_countdown

def main():
    pygame.init()
    pygame.mixer.init()

    # dimensões da tela
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Pixel Racer Championship")
    clock = pygame.time.Clock()

    # carrega sons
    try:
        engine_sound = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'engine.mp3'))
        crash_sound = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'crash.mp3'))
        boost_sound = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'boost.mp3'))
        lap_sound = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'lap.mp3'))
        pygame.mixer.music.load(os.path.join(AUDIO_DIR, 'race_music.mp3'))
        pygame.mixer.music.set_volume(0.5)
        sound_available = True
    except:
        sound_available = False
        print("Arquivos de som não encontrados. Continuando sem som.")

    # fontes
    try:
        font_small = load_font('PressStart2P-Regular.ttf', 20)
        font_huge = load_font('PressStart2P-Regular.ttf', 60)
    except:
        font_small = pygame.font.Font(None, 40)
        font_huge = pygame.font.Font(None, 100)

    # carrega foto da pista
    track_mask = pygame.image.load(os.path.join(IMAGE_DIR, "track_mask3.png")).convert()
    track_mask = pygame.transform.scale(track_mask, (COLS, ROWS))

    # gera tiles
    grass_tiles = generate_grass_tiles()
    track_tiles = generate_track_tiles()
    curb_tile = generate_curb_tile()

    # gera tilemap e grass_map
    tilemap = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    grass_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            color = track_mask.get_at((x, y))[:3]
            if color == (40, 40, 40):
                tilemap[y][x] = 1
            elif color == (34, 177, 76):
                tilemap[y][x] = 0
            elif color == (255, 0, 0):
                tilemap[y][x] = 2
            elif color == (0, 0, 255):
                tilemap[y][x] = 4
            elif color == (255, 255, 255):
                tilemap[y][x] = 5
            elif color == (100, 100, 100):
                tilemap[y][x] = 6
            elif color == (150, 150, 150):
                tilemap[y][x] = 7
            else:
                tilemap[y][x] = 0
            if tilemap[y][x] == 0 or tilemap[y][x] == 2:
                grass_map[y][x] = random.randrange(len(grass_tiles))

    # sistema de partículas
    particle_system = ParticleSystem()

    game_state = "intro"
    winner_num = None
    cars = []
    countdown = 3
    last_tick = pygame.time.get_ticks()

    if sound_available:
        pygame.mixer.music.play(-1)

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
                    start_x = 1092
                    start_y = 255
                    spacing = 30
                    car1 = Car(start_x - spacing, start_y, RED, controls1, 1)
                    car1.angle = 90
                    car2 = Car(start_x + spacing, start_y, BLUE, controls2, 2)
                    car2.angle = 90
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
                elif game_state == "winner":
                    if event.key == pygame.K_q:
                        if sound_available:
                            pygame.mixer.music.stop()
                            engine_sound.stop()
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
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
                car.update(cars, tilemap, grass_map, sound_available, engine_sound, crash_sound, boost_sound, lap_sound, particle_system)
            # Vitória por voltas
            for car in cars:
                if car.laps >= LAPS_TO_WIN:
                    game_state = "winner"
                    winner_num = car.player_num
                    if sound_available:
                        pygame.mixer.music.stop()
                        engine_sound.stop()
        particle_system.update()
        # desenha tudo
        screen.fill(BLACK)
        # tela de vitória
        if game_state == "winner":
            # bloqueia desenhos normais, só mostra a imagem de vitória
            screen.fill(BLACK)
            img = pygame.image.load(os.path.join(IMAGE_DIR, f"player{winner_num}_win.png")).convert_alpha()
            img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(img, (0, 0))
        else:
            if game_state == "intro":
                draw_intro(screen)
            else:
                draw_track(screen, tilemap, grass_map, track_tiles, grass_tiles, curb_tile)
                if game_state in ["countdown", "racing"]:
                    for car in cars:
                        car.draw(screen)
                        # Efeito visual do turbo
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
                if game_state in ["countdown", "racing"] and cars:
                    draw_hud(screen, cars, font_small)
                if game_state == "countdown":
                    draw_countdown(screen, countdown, font_huge)
                controls_text = font_small.render("WASD/SETA PARA MOVER, SHIFT/CTRL PARA TURBO", True, BLACK)
                screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 40))
        if game_state not in ["intro"]:
            for car in cars:
                car.draw_skid_marks(screen)
            particle_system.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
