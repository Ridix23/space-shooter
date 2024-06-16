import pygame
import random
import sys
import os
from auth import login, register, save_score, get_top_scores
from database import create_tables, create_connection

# Инициализация Pygame
pygame.init()

# Параметры экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Shooter")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 192, 203)
GREY = (169, 169, 169)

# Шрифты
font = pygame.font.Font(None, 36)

# Создание таблиц базы данных
create_tables()

# Игровые объекты
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (45, 45))  # Уменьшение размера модели игрока
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height - 50)
        self.speed = 5
        self.invincible = False
        self.invincible_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Ограничение движения игрока в пределах экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

        # Обработка состояния неуязвимости
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_time > 2000:  # Неуязвимость длится 2 секунды
                self.invincible = False
                self.image.set_alpha(255)  # Восстановить полную непрозрачность

    def take_damage(self):
        self.invincible = True
        self.invincible_time = pygame.time.get_ticks()
        self.image.set_alpha(128)  # Сделать корабль полупрозрачным

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(20, 70)
        self.image = pygame.image.load('images/meteor.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - size)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(6, 10)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(6, 10)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Heart(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/heart.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (45, 30))  # Уменьшение размера сердца, если необходимо
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = 3.5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.kill()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def load_user():
    if os.path.exists("user.txt"):
        with open("user.txt", "r") as file:
            return int(file.read().strip())
    return None

def save_user(user_id):
    with open("user.txt", "w") as file:
        file.write(str(user_id))

def delete_user():
    if os.path.exists("user.txt"):
        os.remove("user.txt")

# Основное меню
def main_menu():
    user_id = load_user()
    show_main_menu(user_id)

def show_main_menu(user_id=None):
    button_color = WHITE
    button_hover_color = GREEN
    button_click_color = BLUE
    buttons = [
        {"text": "Play" if user_id else "Login", "rect": pygame.Rect(20, 60, 200, 40), "action": "game" if user_id else "login"},
        {"text": "Register", "rect": pygame.Rect(20, 100, 200, 40), "action": "register"},
        {"text": "High Scores", "rect": pygame.Rect(20, 140, 200, 40), "action": "high_scores"},
        {"text": "Logout" if user_id else "Exit", "rect": pygame.Rect(20, 180, 200, 40), "action": "logout" if user_id else sys.exit}
    ]

    email = get_user_email(user_id) if user_id else None

    while True:
        screen.fill(BLACK)
        draw_text('Main Menu', font, WHITE, screen, 20, 20)

        if email:
            draw_text(email, font, WHITE, screen, screen_width - 250, 10)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for button in buttons:
            color = button_color
            if button["rect"].collidepoint(mouse_pos):
                color = button_hover_color
                if mouse_click[0]:
                    color = button_click_color
                    action = button["action"]
                    if action == "login":
                        login_screen()
                    elif action == "register":
                        register_screen()
                    elif action == "high_scores":
                        high_scores_screen(user_id)
                    elif action == "game":
                        game(user_id)
                    elif action == "logout":
                        delete_user()
                        show_main_menu()
                    else:
                        action()

            pygame.draw.rect(screen, color, button["rect"])
            draw_text(button["text"], font, BLACK, screen, button["rect"].x + 10, button["rect"].y + 10)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def login_screen():
    email = ""
    password = ""
    input_active = None
    message = ""

    while True:
        screen.fill(BLACK)
        draw_text('Login', font, WHITE, screen, 20, 20)
        draw_text('Email:', font, WHITE, screen, 20, 100)
        pygame.draw.rect(screen, GREY if input_active == "email" else WHITE, (150, 100, 500, 30), 2)
        draw_text(email, font, WHITE, screen, 160, 100)

        draw_text('Password:', font, WHITE, screen, 20, 150)
        pygame.draw.rect(screen, GREY if input_active == "password" else WHITE, (150, 150, 500, 30), 2)
        draw_text('*' * len(password), font, WHITE, screen, 160, 150)

        draw_text(message, font, RED, screen, 20, 250)

        login_button = pygame.Rect(20, 300, 200, 40)
        pygame.draw.rect(screen, WHITE, login_button)
        draw_text('Login', font, BLACK, screen, login_button.x + 10, login_button.y + 10)

        back_button = pygame.Rect(20, 350, 200, 40)
        pygame.draw.rect(screen, WHITE, back_button)
        draw_text('Back', font, BLACK, screen, back_button.x + 10, back_button.y + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if input_active == "email":
                    if event.key == pygame.K_BACKSPACE:
                        email = email[:-1]
                    elif event.key != pygame.K_RETURN:
                        email += event.unicode
                elif input_active == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    elif event.key != pygame.K_RETURN:
                        password += event.unicode
                if event.key == pygame.K_RETURN:
                    user_id, message = login(email, password)
                    if user_id:
                        save_user(user_id)
                        show_main_menu(user_id)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 150 <= event.pos[0] <= 650 and 100 <= event.pos[1] <= 130:
                    input_active = "email"
                elif 150 <= event.pos[0] <= 650 and 150 <= event.pos[1] <= 180:
                    input_active = "password"
                elif login_button.collidepoint(event.pos):
                    user_id, message = login(email, password)
                    if user_id:
                        save_user(user_id)
                        show_main_menu(user_id)
                elif back_button.collidepoint(event.pos):
                    show_main_menu()

        pygame.display.flip()

def register_screen():
    email = ""
    password = ""
    input_active = None
    message = ""

    while True:
        screen.fill(BLACK)
        draw_text('Register', font, WHITE, screen, 20, 20)
        draw_text('Email:', font, WHITE, screen, 20, 100)
        pygame.draw.rect(screen, GREY if input_active == "email" else WHITE, (150, 100, 500, 30), 2)
        draw_text(email, font, WHITE, screen, 160, 100)

        draw_text('Password:', font, WHITE, screen, 20, 150)
        pygame.draw.rect(screen, GREY if input_active == "password" else WHITE, (150, 150, 500, 30), 2)
        draw_text('*' * len(password), font, WHITE, screen, 160, 150)

        draw_text(message, font, RED, screen, 20, 250)

        register_button = pygame.Rect(20, 300, 200, 40)
        pygame.draw.rect(screen, WHITE, register_button)
        draw_text('Register', font, BLACK, screen, register_button.x + 10, register_button.y + 10)

        back_button = pygame.Rect(20, 350, 200, 40)
        pygame.draw.rect(screen, WHITE, back_button)
        draw_text('Back', font, BLACK, screen, back_button.x + 10, back_button.y + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if input_active == "email":
                    if event.key == pygame.K_BACKSPACE:
                        email = email[:-1]
                    elif event.key != pygame.K_RETURN:
                        email += event.unicode
                elif input_active == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    elif event.key != pygame.K_RETURN:
                        password += event.unicode
                if event.key == pygame.K_RETURN:
                    message = register(email, password)
                    if message == "Registration successful!":
                        show_main_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 150 <= event.pos[0] <= 650 and 100 <= event.pos[1] <= 130:
                    input_active = "email"
                elif 150 <= event.pos[0] <= 650 and 150 <= event.pos[1] <= 180:
                    input_active = "password"
                elif register_button.collidepoint(event.pos):
                    message = register(email, password)
                    if message == "Registration successful!":
                        show_main_menu()
                elif back_button.collidepoint(event.pos):
                    show_main_menu()

        pygame.display.flip()

def high_scores_screen(user_id):
    top_scores = get_top_scores()

    while True:
        screen.fill(BLACK)
        draw_text('High Scores', font, WHITE, screen, 20, 20)

        for idx, (email, score, date) in enumerate(top_scores):
            draw_text(f"{idx + 1}. {email} - {score} - {date}", font, WHITE, screen, 20, 60 + idx * 30)

        draw_text('Back', font, WHITE, screen, 20, 400)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_main_menu(user_id)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 10 <= event.pos[0] <= 50 and 400 <= event.pos[1] <= 440:
                    show_main_menu(user_id)

        pygame.display.flip()

def get_user_email(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    email = cursor.fetchone()[0]
    conn.close()
    return email

    # Игра
def game(user_id):
    all_sprites = pygame.sprite.Group()
    meteors = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    hearts = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for i in range(10):
        meteor = Meteor()
        all_sprites.add(meteor)
        meteors.add(meteor)

    running = True
    clock = pygame.time.Clock()
    lives = 3
    score = 0
    start_time = pygame.time.get_ticks()
    last_heart_spawn_time = pygame.time.get_ticks()

    background = pygame.image.load('images/spaceback.png').convert()
    background_rect1 = background.get_rect()
    background_rect2 = background.get_rect()
    background_rect2.y = -background_rect2.height

    def show_game_over():
        nonlocal running
        running = False
        while True:
            screen.fill(BLACK)
            draw_text('Game Over', font, RED, screen, screen_width // 2 - 80, screen_height // 2 - 40)
            try_again_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2, 200, 40)
            menu_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 40)
            pygame.draw.rect(screen, WHITE, try_again_button)
            pygame.draw.rect(screen, WHITE, menu_button)
            draw_text('Try Again', font, BLACK, screen, try_again_button.x + 10, try_again_button.y + 10)
            draw_text('Menu', font, BLACK, screen, menu_button.x + 10, menu_button.y + 10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if try_again_button.collidepoint(event.pos):
                        game(user_id)
                    elif menu_button.collidepoint(event.pos):
                        show_main_menu(user_id)

            pygame.display.flip()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if screen_width - 110 <= event.pos[0] <= screen_width - 10 and 10 <= event.pos[1] <= 40:
                    delete_user()
                    show_main_menu()

        all_sprites.update()

        background_rect1.y += 0.7
        background_rect2.y += 0.7
        if background_rect1.top >= screen_height:
            background_rect1.y = background_rect2.y - background_rect1.height
        if background_rect2.top >= screen_height:
            background_rect2.y = background_rect1.y - background_rect2.height

        hits = pygame.sprite.groupcollide(meteors, bullets, True, True)
        for hit in hits:
            score += 1
            meteor = Meteor()
            all_sprites.add(meteor)
            meteors.add(meteor)

        if not player.invincible and pygame.sprite.spritecollideany(player, meteors):
            lives -= 1
            player.take_damage()
            if lives == 0:
                save_score(user_id, score)
                show_game_over()

        heart_hits = pygame.sprite.spritecollide(player, hearts, True)
        for heart in heart_hits:
            lives += 1

        current_time = pygame.time.get_ticks()
        if current_time - last_heart_spawn_time > 10000:
            heart = Heart()
            all_sprites.add(heart)
            hearts.add(heart)
            last_heart_spawn_time = current_time

        elapsed_time = (current_time - start_time) // 1000

        screen.fill(BLACK)
        screen.blit(background, background_rect1)
        screen.blit(background, background_rect2)
        all_sprites.draw(screen)

        draw_text(f'Lives: {lives}', font, WHITE, screen, 10, 10)
        draw_text(f'Score: {score}', font, WHITE, screen, 10, 40)
        draw_text(f'Time: {elapsed_time}s', font, WHITE, screen, 10, 70)

        pygame.display.flip()

        clock.tick(60)


# Запуск основного меню
main_menu()