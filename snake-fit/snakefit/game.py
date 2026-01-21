import random
import pygame
from pathlib import Path

import snakefit.config as cfg
from snakefit.input_keyboard import KeyboardInput
from snakefit.highscores import (
    load_highscores,
    save_highscores,
    maybe_add_highscore,
    is_highscore,
)

# =================================================
# PATHS (snakefit/assets)
# =================================================
BASE_DIR = Path(__file__).resolve().parent          # snakefit/
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# =================================================
# INIT
# =================================================
pygame.init()
pygame.mixer.init()

WIDTH = cfg.GRID_WIDTH * cfg.CELL_SIZE
HEIGHT = cfg.GRID_HEIGHT * cfg.CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake-Fit")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)
mid_font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

keyboard = KeyboardInput()

# =================================================
# AUDIO (pygame braucht str())
# =================================================
sound_enabled = True
music_enabled = True

SND_EAT = pygame.mixer.Sound(str(SOUNDS_DIR / "snd_eat.mp3"))
SND_BONUS = pygame.mixer.Sound(str(SOUNDS_DIR / "snd_bonus.mp3"))
SND_BAD = pygame.mixer.Sound(str(SOUNDS_DIR / "snd_bad.mp3"))
SND_DEAD = pygame.mixer.Sound(str(SOUNDS_DIR / "snd_dead.mp3"))
SND_HIGHSCORE = pygame.mixer.Sound(str(SOUNDS_DIR / "snd_highscore.mp3"))

for s in (SND_EAT, SND_BONUS, SND_BAD, SND_DEAD, SND_HIGHSCORE):
    s.set_volume(0.4)

pygame.mixer.music.load(str(SOUNDS_DIR / "music.mp3"))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

def play(sound):
    if sound_enabled:
        sound.play()

# =================================================
# STATES / MODES
# =================================================
STATE_MENU = "MENU"
STATE_RUNNING = "RUNNING"
STATE_GAME_OVER = "GAME_OVER"
STATE_NAME_INPUT = "NAME_INPUT"
STATE_HIGHSCORES = "HIGHSCORES"

state = STATE_MENU
game_mode = "NORMAL"   # NORMAL | HARDCORE

# =================================================
# MENU
# =================================================
menu_items = [
    "Start Game",
    "Start Hardcore",
    "Highscores",
    "Sound: ON",
    "Music: ON",
    "Quit",
]
menu_index = 0

# =================================================
# DATA
# =================================================
highscores = load_highscores()
player_name = ""
god_mode = False

# =================================================
# HELPERS
# =================================================
def spawn_food(snake):
    while True:
        p = (
            random.randint(0, cfg.GRID_WIDTH - 1),
            random.randint(0, cfg.GRID_HEIGHT - 1),
        )
        if p not in snake:
            return p

def reset_game():
    snake = [(5, 5), (4, 5), (3, 5)]
    direction = "RIGHT"
    food = spawn_food(snake)
    return snake, direction, food

def draw_cell(pos, color):
    x, y = pos
    r = pygame.Rect(
        x * cfg.CELL_SIZE + 2,
        y * cfg.CELL_SIZE + 2,
        cfg.CELL_SIZE - 4,
        cfg.CELL_SIZE - 4,
    )
    pygame.draw.rect(screen, color, r, border_radius=8)

def draw_head(pos, direction):
    x, y = pos
    cx = x * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
    cy = y * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
    r = cfg.CELL_SIZE // 2 - 2

    color = (255, 200, 80) if god_mode else (0, 220, 0)
    pygame.draw.circle(screen, color, (cx, cy), r)

    eye = r // 2
    eyes = {
        "UP":    [(-eye, -eye), (eye, -eye)],
        "DOWN":  [(-eye, eye), (eye, eye)],
        "LEFT":  [(-eye, -eye), (-eye, eye)],
        "RIGHT": [(eye, -eye), (eye, eye)],
    }
    for ox, oy in eyes[direction]:
        pygame.draw.circle(screen, (10, 10, 10), (cx + ox, cy + oy), 3)

# =================================================
# GAME INIT
# =================================================
snake, direction, food = reset_game()
last_tick = pygame.time.get_ticks()

# =================================================
# MAIN LOOP
# =================================================
running = True
while running:
    clock.tick(cfg.FPS)

    # CHEAT – nur NORMAL
    if state == STATE_RUNNING and game_mode == "NORMAL":
        k = pygame.key.get_pressed()
        if k[pygame.K_i] and k[pygame.K_l] and k[pygame.K_m]:
            god_mode = not god_mode
            pygame.time.wait(300)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        # ---------------- MENU ----------------
        if state == STATE_MENU and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP:
                menu_index = (menu_index - 1) % len(menu_items)
            elif e.key == pygame.K_DOWN:
                menu_index = (menu_index + 1) % len(menu_items)
            elif e.key == pygame.K_RETURN:
                choice = menu_items[menu_index]

                if choice == "Start Game":
                    game_mode = "NORMAL"
                    god_mode = False
                    snake, direction, food = reset_game()
                    state = STATE_RUNNING

                elif choice == "Start Hardcore":
                    game_mode = "HARDCORE"
                    god_mode = False
                    snake, direction, food = reset_game()
                    state = STATE_RUNNING

                elif choice == "Highscores":
                    state = STATE_HIGHSCORES

                elif choice.startswith("Sound"):
                    sound_enabled = not sound_enabled
                    menu_items[3] = f"Sound: {'ON' if sound_enabled else 'OFF'}"

                elif choice.startswith("Music"):
                    music_enabled = not music_enabled
                    menu_items[4] = f"Music: {'ON' if music_enabled else 'OFF'}"
                    if music_enabled:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()

                else:
                    running = False

        # ------------- GAME OVER --------------
        elif state == STATE_GAME_OVER and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                snake, direction, food = reset_game()
                state = STATE_RUNNING
            elif e.key == pygame.K_RETURN and is_highscore(highscores, len(snake), game_mode):
                player_name = ""
                state = STATE_NAME_INPUT
                play(SND_HIGHSCORE)
            elif e.key == pygame.K_ESCAPE:
                state = STATE_MENU

        # ------------ NAME INPUT --------------
        elif state == STATE_NAME_INPUT and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                highscores = maybe_add_highscore(
                    highscores,
                    player_name or "ANON",
                    len(snake),
                    game_mode,
                )
                save_highscores(highscores)
                state = STATE_MENU
            elif e.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            elif e.unicode.isprintable() and len(player_name) < cfg.MAX_NAME_LENGTH:
                player_name += e.unicode.upper()

        # ------------ HIGHSCORES --------------
        elif state == STATE_HIGHSCORES and e.type == pygame.KEYDOWN:
            state = STATE_MENU

    # ---------------- GAME LOGIC ----------------
    if state == STATE_RUNNING:
        new_dir = keyboard.get_direction({
            "UP": pygame.key.get_pressed()[pygame.K_UP],
            "DOWN": pygame.key.get_pressed()[pygame.K_DOWN],
            "LEFT": pygame.key.get_pressed()[pygame.K_LEFT],
            "RIGHT": pygame.key.get_pressed()[pygame.K_RIGHT],
        })
        if new_dir:
            direction = new_dir

        now = pygame.time.get_ticks()
        if now - last_tick >= cfg.SNAKE_TICK_MS:
            last_tick = now
            hx, hy = snake[0]

            if direction == "UP": hy -= 1
            elif direction == "DOWN": hy += 1
            elif direction == "LEFT": hx -= 1
            elif direction == "RIGHT": hx += 1

            if game_mode == "HARDCORE":
                if hx < 0 or hx >= cfg.GRID_WIDTH or hy < 0 or hy >= cfg.GRID_HEIGHT:
                    play(SND_DEAD)
                    state = STATE_GAME_OVER
                    continue
            else:
                hx %= cfg.GRID_WIDTH
                hy %= cfg.GRID_HEIGHT

            new_head = (hx, hy)

            if new_head in snake and not god_mode:
                play(SND_DEAD)
                state = STATE_GAME_OVER
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    play(SND_EAT)
                    food = spawn_food(snake)
                else:
                    snake.pop()

    # ---------------- RENDER ----------------
    screen.fill((0, 0, 0))

    if state == STATE_MENU:
        title = big_font.render("SNAKE-FIT", True, (0, 220, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
        y = HEIGHT // 2 - 20
        for i, item in enumerate(menu_items):
            p = "> " if i == menu_index else "  "
            txt = mid_font.render(p + item, True, (200, 200, 200))
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))
            y += 36

    elif state == STATE_HIGHSCORES:
        title = mid_font.render("TOP 20 HIGHSCORES", True, (220, 220, 220))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))
        y = 110
        for i, hs in enumerate(highscores):
            mode = hs.get("mode", "NORMAL")
            prefix = "[HC] " if mode == "HARDCORE" else ""
            txt = font.render(
                f"{i+1:>2}. {prefix}{hs['name']}   {hs['score']}",
                True, (180, 180, 180),
            )
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))
            y += 22

    else:
        draw_cell(food, (200, 50, 50))
        for seg in snake[1:]:
            draw_cell(seg, (0, 180, 0))
        draw_head(snake[0], direction)

        screen.blit(font.render(f"Score: {len(snake)}", True, (220, 220, 220)), (8, 8))

        if highscores:
            best = highscores[0]
            mode = best.get("mode", "NORMAL")
            tag = "[HC] " if mode == "HARDCORE" else ""
            screen.blit(
                font.render(
                    f"#1 {tag}{best['name']} – {best['score']}",
                    True, (160, 160, 160),
                ),
                (8, 30),
            )

        if state == STATE_GAME_OVER:
            title = big_font.render("GAME OVER", True, (220, 60, 60))
            hint = font.render("R = Retry | ENTER = Save | ESC = Menu", True, (200, 200, 200))
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    if state == STATE_NAME_INPUT:
        title = mid_font.render("NEW HIGHSCORE!", True, (0, 220, 0))
        prompt = font.render("ENTER YOUR NAME", True, (200, 200, 200))
        name = big_font.render(player_name + "_", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
        screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        screen.blit(name, name.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

    pygame.display.flip()

pygame.quit()
