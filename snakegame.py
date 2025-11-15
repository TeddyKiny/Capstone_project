# Building a Snake Game using Pygame
#importing necessary libraries
import pygame
import random
import csv
import os
import string
import numpy as np

# Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)

# Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game :)')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)
tiny_font = pygame.font.SysFont(None, 24)

# Files
HIGHSCORES_FILE = 'highscores.csv'
PLAYER_DATA_FILE = 'player_data.csv'

# Snake types
snakes = {
    0: {'name': 'Classic Green', 'color': GREEN, 'start_len': 3, 'speed_bonus': 0, 'doubloons_mult': 1, 'price': 0},
    1: {'name': 'Speedy Red', 'color': RED, 'start_len': 3, 'speed_bonus': 3, 'doubloons_mult': 1, 'price': 100},
    2: {'name': 'Bulky Blue', 'color': BLUE, 'start_len': 5, 'speed_bonus': -1, 'doubloons_mult': 1, 'price': 200},
    3: {'name': 'Golden', 'color': GOLD, 'start_len': 4, 'speed_bonus': 1, 'doubloons_mult': 2, 'price': 500}
}

# sound effects
def create_beep(frequency=440, duration=0.1, volume=0.5):
    sample_rate = pygame.mixer.get_init()[0]
    samples = int(sample_rate * duration)
    period = sample_rate // frequency
    wave = []
    for i in range(samples):
        value = int(32767 * volume * ((i // period) % 2))  
        wave.append([value, value])  
    arr = np.array(wave, dtype=np.int16)
    return pygame.sndarray.make_sound(arr)

# Create sounds
eat_sound = create_beep(800, 0.08, 0.5)
collision_sound = create_beep(200, 0.3, 0.5)
# High Scores File Creation
def create_highscores_file():
    if not os.path.exists(HIGHSCORES_FILE):
        with open(HIGHSCORES_FILE, 'w', newline='') as f:
            csv.writer(f).writerow(['Name', 'Score'])

# Load high scores
def load_highscores():
    scores = []
    try:
        with open(HIGHSCORES_FILE, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    scores.append((row[0], int(row[1])))
    except Exception:
        pass
    return sorted(scores, key=lambda x: x[1], reverse=True)[:10]

# Save high score
def save_highscore(name, score):
    scores = load_highscores()
    scores.append((name, score))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
    with open(HIGHSCORES_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Score'])
        writer.writerows(scores)

# Load player data
def load_player_data():
    if not os.path.exists(PLAYER_DATA_FILE):
        return {'doubloons': 50, 'selected': 0, 'unlocked': {0}}
    try:
        with open(PLAYER_DATA_FILE, 'r') as f:
            reader = csv.reader(f)
            row = next(reader)
            doubloons = int(row[0])
            selected = int(row[1])
            unlocked = set(map(int, row[2].split(','))) if len(row) > 2 and row[2] else {0}
            return {'doubloons': doubloons, 'selected': selected, 'unlocked': unlocked}
    except Exception:
        return {'doubloons': 50, 'selected': 0, 'unlocked': {0}}
 
 
def save_player_data(data):
    unlocked_str = ','.join(map(str, sorted(data['unlocked'])))
    with open(PLAYER_DATA_FILE, 'w', newline='') as f:
        csv.writer(f).writerow([data['doubloons'], data['selected'], unlocked_str])

# === Rendering ===
def draw_text(text, font_obj, color, x, y):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

# Menus 
def main_menu(data):
    while True:
        screen.fill(BLACK)
        draw_text('Snake Game', font, WHITE, WIDTH // 2, 100)
        draw_text(f'Doubloons: {data["doubloons"]}', small_font, GREEN, WIDTH // 2, 160)
        draw_text(f"Current: {snakes[data['selected']]['name']}", small_font, BLUE, WIDTH // 2, 200)
        draw_text('SPACE: Play', small_font, BLUE, WIDTH // 2, 260)
        draw_text('S: Shop', small_font, WHITE, WIDTH // 2, 300)
        draw_text('H: High Scores', small_font, WHITE, WIDTH // 2, 340)
        draw_text('Q: Quit', small_font, WHITE, WIDTH // 2, 380)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return 'play'
                if event.key == pygame.K_s: return 'shop'
                if event.key == pygame.K_h: show_highscores()
                if event.key == pygame.K_q: return 'quit'
        clock.tick(60)

# High Scores Display
def show_highscores():
    highscores = load_highscores()
    while True:
        screen.fill(BLACK)
        draw_text('HIGH SCORES', font, WHITE, WIDTH // 2, 100)
        draw_text('SPACE: Back', small_font, BLUE, WIDTH // 2, HEIGHT - 100)
        for i, (n, s) in enumerate(highscores):
            color = GOLD if i == 0 else GREEN if i < 3 else WHITE
            draw_text(f'{i+1}. {n}: {s}', small_font, color, WIDTH // 2, 180 + i * 40)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                return
        clock.tick(60)

# Snake Shop Menu
def shop_menu(data):
    snakes_list = list(snakes.keys())
    sel = 0
    while True:
        screen.fill(BLACK)
        draw_text('SNAKE SHOP', font, WHITE, WIDTH // 2, 80)
        draw_text(f'Doubloons: {data["doubloons"]}', small_font, GREEN, WIDTH // 2, 130)
        for j, i in enumerate(snakes_list):
            st = snakes[i]
            owned = i in data['unlocked']
            text = f"> {st['name']}" if j == sel else st['name']
            text += ' (Owned)' if owned else f' - {st["price"]} doubloons'
            color = BLUE if j == sel else GREEN if owned else WHITE
            draw_text(text, small_font, color, WIDTH // 2, 200 + j * 50)
        draw_text('↑↓: Move  ENTER: Buy/Select  SPACE: Back', tiny_font, WHITE, WIDTH // 2, HEIGHT - 80)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return data
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: sel = (sel - 1) % len(snakes_list)
                elif event.key == pygame.K_DOWN: sel = (sel + 1) % len(snakes_list)
                elif event.key == pygame.K_RETURN:
                    i = snakes_list[sel]
                    if i in data['unlocked']:
                        data['selected'] = i
                    elif data['doubloons'] >= snakes[i]['price']:
                        data['doubloons'] -= snakes[i]['price']
                        data['unlocked'].add(i)
                        data['selected'] = i
                    save_player_data(data)
                elif event.key == pygame.K_SPACE:
                    return data
        clock.tick(60)

#player name for high score
def get_name(score):
    name = ''
    blink = 0
    while True:
        blink += 1
        screen.fill(BLACK)
        draw_text(f'New High Score: {score}!', font, GREEN, WIDTH // 2, HEIGHT // 2 - 100)
        draw_text('Enter Name (max 10 chars):', small_font, WHITE, WIDTH // 2, HEIGHT // 2 - 30)
        display = name + ('|' if blink % 60 < 30 else '')
        draw_text(display, font, WHITE, WIDTH // 2, HEIGHT // 2 + 30)
        draw_text('ENTER: Save  BACKSPACE: Delete', tiny_font, WHITE, WIDTH // 2, HEIGHT // 2 + 80)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'PLAYER'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return (name or 'PLAYER').upper()
                if event.key == pygame.K_BACKSPACE: name = name[:-1]
                elif len(name) < 10 and event.unicode.isalpha(): name += event.unicode.upper()
        clock.tick(60)

#game over screen
def game_over(score):
    highscores = load_highscores()
    is_new = (score > 0) and (len(highscores) < 10 or score > highscores[-1][1])
    name = 'PLAYER'
    if is_new:
        name = get_name(score)
        save_highscore(name, score)
        highscores = load_highscores()

    while True:
        screen.fill(BLACK)
        draw_text('GAME OVER', font, RED, WIDTH // 2, HEIGHT // 2 - 120)
        draw_text(f'Score: {score}', small_font, WHITE, WIDTH // 2, HEIGHT // 2 - 70)
        draw_text('Top 10:', small_font, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
        for i, (n, s) in enumerate(highscores):
            color = GOLD if n == name and s == score else WHITE
            draw_text(f'{i+1}. {n}: {s}', tiny_font, color, WIDTH // 2, HEIGHT // 2 + 20 + i * 25)
        draw_text('SPACE: Menu', small_font, BLUE, WIDTH // 2, HEIGHT - 100)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                return
        clock.tick(60)

# Main Main Game Loop
def play_game(snake_type):
    color = snake_type['color']
    start_len = snake_type['start_len']
    speed_bonus = snake_type['speed_bonus']
    mult = snake_type['doubloons_mult']
    center_x = (WIDTH // 2 // BLOCK_SIZE) * BLOCK_SIZE
    head_y = (HEIGHT // 2 // BLOCK_SIZE) * BLOCK_SIZE
    snake = [ (center_x - (start_len - 1 - i) * BLOCK_SIZE, head_y) for i in range(start_len) ]

    # initial movement 
    dx, dy = BLOCK_SIZE, 0
    score = 0
    level = 1
    base_speed = 8 + speed_bonus

    # food spawning
    def spawn_food(power_up=0.1):
        color = YELLOW if random.random() < power_up else RED
        while True:
            fx = (random.randrange(0, WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            fy = (random.randrange(0, HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            if (fx, fy) not in snake:
                return fx, fy, color

    food_x, food_y, food_color = spawn_food()
    paused = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_q and paused:
                    return score
                if not paused:
                    if event.key == pygame.K_LEFT and dx != BLOCK_SIZE:
                        dx, dy = -BLOCK_SIZE, 0
                    elif event.key == pygame.K_RIGHT and dx != -BLOCK_SIZE:
                        dx, dy = BLOCK_SIZE, 0
                    elif event.key == pygame.K_UP and dy != BLOCK_SIZE:
                        dx, dy = 0, -BLOCK_SIZE
                    elif event.key == pygame.K_DOWN and dy != -BLOCK_SIZE:
                        dx, dy = 0, BLOCK_SIZE

        # pausing the game
        if paused:
            draw_text('PAUSED', font, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text('P: Resume  Q: Quit', tiny_font, WHITE, WIDTH // 2, HEIGHT // 2 + 50)
            pygame.display.flip()
            clock.tick(5)
            continue

        # Movement
        head_x = snake[-1][0] + dx
        head_y = snake[-1][1] + dy
        new_head = (head_x, head_y)
        snake.append(new_head)

        # Eat food
        if head_x == food_x and head_y == food_y:
            score += 20 if food_color == YELLOW else 10
            eat_sound.play()
            food_x, food_y, food_color = spawn_food()
        else:
            snake.pop(0)

        # Level and speed
        new_level = score // 50 + 1
        if new_level > level:
            level = new_level
        speed = base_speed + (level - 1) * 2

        # Collision detection
        if (head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT or
            new_head in snake[:-1]):
            collision_sound.play()
            return score

        screen.fill(BLACK)

        # HUD
        hud = pygame.Surface((260, 120))
        hud.set_alpha(180)
        hud.fill((20, 20, 20))
        screen.blit(hud, (0, 0))
        draw_text(f'Score: {score}  Level: {level}', small_font, WHITE, 90, 50)
        draw_text(f'Snake: {snake_type["name"]}', tiny_font, BLUE, 90, 80)
        draw_text(f'Earned: {score // 10 * mult}', tiny_font, GOLD, 90, 105)

        pygame.draw.rect(screen, food_color, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])
        for seg in snake:
            pygame.draw.rect(screen, color, [*seg, BLOCK_SIZE, BLOCK_SIZE])
        pygame.display.flip()
        clock.tick(speed)


#Main Loop
def main():
    create_highscores_file()
    data = load_player_data()
    while True:
        choice = main_menu(data)
        if choice == 'quit':
            break
        if choice == 'play':
            snake_type = snakes[data['selected']]
            score = play_game(snake_type)
            data['doubloons'] += (score // 10) * snake_type['doubloons_mult']
            save_player_data(data)
            game_over(score)
        elif choice == 'shop':
            data = shop_menu(data)
    pygame.quit()

if __name__ == '__main__':
    main()