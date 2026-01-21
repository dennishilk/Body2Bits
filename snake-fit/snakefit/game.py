import random
import pygame
import snakefit.config as cfg
from pathlib import Path

from snakefit.input_keyboard import KeyboardInput
from snakefit.highscores import (
    load_highscores,
    save_highscores,
    maybe_add_highscore,
    is_highscore,
)

# -------------------------------------------------
# Init
# -------------------------------------------------
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

# -------------------------------------------------
# Assets
# -------------------------------------------------
ASSETS = Path(__file__).parent / "assets"
SOUNDS = ASSETS / "sounds"

def load_icon(name):
    return pygame.image.load(ASSETS / name).convert_alpha()

def load_sound(name):
    return pygame.mixer.Sound(SOUNDS / name)

ICON_APPLE  = load_icon("apple.png")
ICON_BANANA = load_icon("banana.png")
ICON_SKULL  = load_icon("skull.png")

SND_EAT = load_sound("snd_eat.mp3")
SND_BONUS = load_sound("snd_bonus.mp3")
SND_BAD = load_sound("snd_bad.mp3")
SND_DEAD = load_sound("snd_dead.mp3")
SND_HIGHSCORE = load_sound("snd_eat.mp3")

for s in (SND_EAT, SND_BONUS, SND_BAD, SND_DEAD, SND_HIGHSCORE):
    s.set_volume(1)

# Background Music
MUSIC_FILE = SOUNDS / "music.mp3"

# -------------------------------------------------
# States
# -------------------------------------------------
STATE_MENU = "MENU"
STATE_RUNNING = "RUNNING"
STATE_GAME_OVER = "GAME_OVER"
STATE_NAME_INPUT = "NAME_INPUT"
STATE_HIGHSCORES = "HIGHSCORES"

state = STATE_MENU

# -------------------------------------------------
# Data
# -------------------------------------------------
sound_enabled = True
music_enabled = True

menu_items = [
    "Start Game",
    "Highscores",
    "Sound: ON",
    "Music: ON",
    "Quit",
]
menu_index = 0

highscores = load_highscores()
player_name = ""
god_mode = False

# -------------------------------------------------
# Food setup
# -------------------------------------------------
FOOD_NORMAL = "NORMAL"
FOOD_BONUS = "BONUS"
FOOD_BAD = "BAD"

BONUS_LIFETIME_MS = 5000
BAD_LIFETIME_MS = 3000

BONUS_BLINK_MS = 300
BAD_BLINK_MS = 200

FOOD_SCALE = 2.0

food = None
food_type = FOOD_NORMAL
food_spawn_time = 0

damage_text_timer = 0
damage_text_pos = None

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def play(sound):
    if sound_enabled:
        sound.play()

def start_music():
    if music_enabled:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()

def spawn_food(snake):
    while True:
        p = (
            random.randint(0, cfg.GRID_WIDTH - 1),
            random.randint(0, cfg.GRID_HEIGHT - 1),
        )
        if p not in snake:
            return p

def spawn_food_with_type(snake):
    global food_type, food_spawn_time
    food = spawn_food(snake)
    food_spawn_time = pygame.time.get_ticks()

    r = random.random()
    if r < 0.15:
        food_type = FOOD_BONUS
    elif r < 0.25:
        food_type = FOOD_BAD
    else:
        food_type = FOOD_NORMAL

    return food

def reset_game():
    snake = [(5, 5), (4, 5), (3, 5)]
    direction = "RIGHT"
    food = spawn_food_with_type(snake)
    return snake, direction, food

# -------------------------------------------------
# Snake graphics
# -------------------------------------------------
def lerp(a, b, t):
    return int(a + (b - a) * t)

def draw_cell(pos, color, radius=8):
    x, y = pos
    rect = pygame.Rect(
        x * cfg.CELL_SIZE + 2,
        y * cfg.CELL_SIZE + 2,
        cfg.CELL_SIZE - 4,
        cfg.CELL_SIZE - 4,
    )
    pygame.draw.rect(screen, color, rect, border_radius=radius)

def draw_snake(snake, direction):
    length = len(snake)
    for i, seg in enumerate(snake[1:], start=1):
        t = i / max(length - 1, 1)
        col = (lerp(0, 60, t), lerp(200, 120, t), lerp(0, 60, t))
        draw_cell(seg, col, radius=10)
    draw_head(snake[0], direction)

def draw_head(pos, direction):
    x, y = pos
    cx = x * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
    cy = y * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
    r = cfg.CELL_SIZE // 2 - 2

    if god_mode:
        for g in range(6, 14, 2):
            pygame.draw.circle(screen, (255, 200, 80), (cx, cy), r + g, 1)
        color = (255, 215, 80)
    else:
        color = (0, 220, 0)

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

# -------------------------------------------------
# Food rendering
# -------------------------------------------------
def draw_food():
    x, y = food
    cx = x * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
    cy = y * cfg.CELL_SIZE + cfg.CELL_SIZE // 2

    if food_type == FOOD_NORMAL:
        icon = ICON_APPLE
    elif food_type == FOOD_BONUS:
        if (pygame.time.get_ticks() // BONUS_BLINK_MS) % 2 != 0:
            return
        icon = ICON_BANANA
    else:
        if (pygame.time.get_ticks() // BAD_BLINK_MS) % 2 != 0:
            return
        icon = ICON_SKULL

    size = int(cfg.CELL_SIZE * FOOD_SCALE)
    scaled = pygame.transform.scale(icon, (size, size))
    rect = scaled.get_rect(center=(cx, cy))
    screen.blit(scaled, rect)

def draw_damage_text():
    global damage_text_timer
    if damage_text_timer > 0 and damage_text_pos:
        x, y = damage_text_pos
        cx = x * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
        cy = y * cfg.CELL_SIZE - damage_text_timer
        txt = font.render("-2", True, (255, 80, 80))
        screen.blit(txt, txt.get_rect(center=(cx, cy)))
        damage_text_timer -= 1

# -------------------------------------------------
# Game init
# -------------------------------------------------
snake, direction, food = reset_game()
last_tick = pygame.time.get_ticks()
start_music()

# -------------------------------------------------
# Main loop
# -------------------------------------------------
running = True
while running:
    clock.tick(cfg.FPS)

    if state == STATE_RUNNING:
        k = pygame.key.get_pressed()
        if k[pygame.K_i] and k[pygame.K_l] and k[pygame.K_m]:
            god_mode = not god_mode
            pygame.time.wait(300)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if state == STATE_MENU and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP:
                menu_index = (menu_index - 1) % len(menu_items)
            elif e.key == pygame.K_DOWN:
                menu_index = (menu_index + 1) % len(menu_items)
            elif e.key == pygame.K_RETURN:
                choice = menu_items[menu_index]

                if choice == "Start Game":
                    snake, direction, food = reset_game()
                    state = STATE_RUNNING

                elif choice == "Highscores":
                    state = STATE_HIGHSCORES

                elif choice.startswith("Sound"):
                    sound_enabled = not sound_enabled
                    menu_items[2] = f"Sound: {'ON' if sound_enabled else 'OFF'}"

                elif choice.startswith("Music"):
                    music_enabled = not music_enabled
                    menu_items[3] = f"Music: {'ON' if music_enabled else 'OFF'}"
                    if music_enabled:
                        start_music()
                    else:
                        stop_music()

                else:
                    running = False

        elif state == STATE_GAME_OVER and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                snake, direction, food = reset_game()
                state = STATE_RUNNING
            elif e.key == pygame.K_RETURN and is_highscore(highscores, len(snake)):
                player_name = ""
                state = STATE_NAME_INPUT
                play(SND_HIGHSCORE)
            elif e.key == pygame.K_ESCAPE:
                state = STATE_MENU

        elif state == STATE_NAME_INPUT and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                highscores = maybe_add_highscore(highscores, player_name or "ANON", len(snake))
                save_highscores(highscores)
                state = STATE_MENU
            elif e.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            elif e.unicode.isprintable() and len(player_name) < cfg.MAX_NAME_LENGTH:
                player_name += e.unicode.upper()

        elif state == STATE_HIGHSCORES and e.type == pygame.KEYDOWN:
            state = STATE_MENU

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

            hx %= cfg.GRID_WIDTH
            hy %= cfg.GRID_HEIGHT
            new_head = (hx, hy)

            if new_head in snake and not god_mode:
                play(SND_DEAD)
                state = STATE_GAME_OVER
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    if food_type == FOOD_BONUS:
                        snake.insert(0, new_head)
                        snake.insert(0, new_head)
                        play(SND_BONUS)
                    elif food_type == FOOD_BAD and not god_mode and len(snake) > 4:
                        snake.pop(); snake.pop()
                        damage_text_timer = 20
                        damage_text_pos = food
                        play(SND_BAD)
                    else:
                        play(SND_EAT)
                    food = spawn_food_with_type(snake)
                else:
                    snake.pop()

        if food_type == FOOD_BONUS and pygame.time.get_ticks() - food_spawn_time > BONUS_LIFETIME_MS:
            food = spawn_food_with_type(snake)

        if food_type == FOOD_BAD and pygame.time.get_ticks() - food_spawn_time > BAD_LIFETIME_MS:
            food = spawn_food_with_type(snake)

    # ---------------- RENDER ----------------
    screen.fill((0, 0, 0))

    if state == STATE_MENU:
        title = big_font.render("SNAKE-FIT", True, (0, 220, 0))
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 90)))
        y = HEIGHT // 2 - 20
        for i, item in enumerate(menu_items):
            p = "> " if i == menu_index else "  "
            txt = mid_font.render(p + item, True, (200, 200, 200))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, y)))
            y += 36

    elif state == STATE_HIGHSCORES:
        title = mid_font.render("TOP 10 HIGHSCORES", True, (220, 220, 220))
        screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))
        y = 110
        for i, hs in enumerate(highscores):
            txt = font.render(f"{i+1}. {hs['name']}   {hs['score']}", True, (180, 180, 180))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, y)))
            y += 24

    else:
        # --- HUD FIRST ---
        screen.blit(font.render(f"Score: {len(snake)}", True, (220, 220, 220)), (8, 8))
        if highscores:
            best = highscores[0]
            screen.blit(
                font.render(f"#1 {best['name']} – {best['score']}", True, (160, 160, 160)),
                (8, 30)
            )

        # --- GAME OBJECTS ON TOP ---
        draw_food()
        draw_snake(snake, direction)
        draw_damage_text()

        if state == STATE_GAME_OVER:
            title = big_font.render("GAME OVER", True, (220, 60, 60))
            hint = font.render("R = Retry | ENTER = Save | ESC = Menu", True, (200, 200, 200))
            screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
            screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))

    if state == STATE_NAME_INPUT:
        title = mid_font.render("NEW HIGHSCORE!", True, (0, 220, 0))
        prompt = font.render("ENTER YOUR NAME", True, (200, 200, 200))
        name = big_font.render(player_name + "_", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
        screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
        screen.blit(name, name.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))

    pygame.display.flip()

pygame.quit()
