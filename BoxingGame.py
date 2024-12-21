import pygame
import mediapipe as mp
import cv2
import random
import time
import math

# Khởi tạo Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Khởi tạo Pygame
pygame.init()

# Kích thước cửa sổ game
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boxing Game with Hand Gestures")

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Nhân vật
player1_img = pygame.image.load("player1.png").convert_alpha()
player2_img = pygame.image.load("player2.png").convert_alpha()
boss_img = pygame.image.load("boss.jpg").convert_alpha()
back_img = pygame.image.load("thunder.png").convert_alpha()

player1_img = pygame.transform.scale(player1_img, (70, 70))
player2_img = pygame.transform.scale(player2_img, (70, 70))
boss_img = pygame.transform.scale(boss_img, (76, 115))
back_img = pygame.transform.scale(back_img, (474, 612))
boss = boss_img.get_rect(center=(WIDTH - 100, HEIGHT // 2))

player1_img = pygame.transform.flip(player1_img, True, False)  # Lật theo chiều ngang
player2_img = pygame.transform.flip(player2_img, True, False)

player1 = player1_img.get_rect(center=(200, 300))
player2 = player2_img.get_rect(center=(600, 400))
back = back_img.get_rect(center=(400, 300))
player1_health = 100
player2_health = 100

bullet_img = pygame.image.load("f.jpg").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (30, 30))

# FPS
clock = pygame.time.Clock()
FPS = 30

cap = cv2.VideoCapture(0)

# Danh sách đạn và thời gian bắn
bullets = []
last_bullet_time = time.time()

# Mức độ khó
DIFFICULTY = "easy"  # Mặc định là easy
difficulty_intervals = {"easy": 5, "medium": 3, "hard": 1}  # Thời gian thay đổi vị trí (giây)
change_position_interval = difficulty_intervals[DIFFICULTY]
last_position_change_time = time.time()
player2_last_position_change = time.time()


def detect_hand_gestures(frame): #Nhận diện cử chỉ tay
    frame = cv2.flip(frame, 1)  # Lật hình ảnh theo chiều ngang
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            # Lấy vị trí các đầu ngón tay
            landmarks = handLms.landmark
            fingers_up = [(landmarks[i].y < landmarks[i - 2].y) for i in [8, 12, 16, 20]]

            # Xác định cử chỉ
            if not any(fingers_up):
                return "Rock", landmarks

    return "Unknown", None

def show_welcome_screen(): #Giao diện chào mừng
    font = pygame.font.SysFont('Comic Sans MS', 50)
    sub_font = pygame.font.SysFont('Comic Sans MS', 30)
    running = True

    while running:
        screen.fill(WHITE) 
        screen.blit(back_img, back.topleft)
        title_text = font.render("BOXING GAME!", True, BLACK)
        start_text = sub_font.render("Press R to Start", True, BLACK)
        exit_text = sub_font.render("Press E to Exit", True, BLACK)

        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

        screen.blit(title_text, title_rect)
        screen.blit(start_text, start_rect)
        screen.blit(exit_text, exit_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_e:
                    pygame.quit()
                    exit()

def choose_game_mode(): #Chọn chế độ chơi, bao gồm Survival và Training
    font = pygame.font.SysFont('Comic Sans MS', 30)
    running = True

    while running:
        screen.fill(WHITE)
        title_text = font.render("Choose Game Mode", True, BLACK)
        survival_text = font.render("1. Survival", True, BLACK)
        training_text = font.render("2. Training", True, BLACK)

        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        survival_rect = survival_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        training_rect = training_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 0))

        screen.blit(title_text, title_rect)
        screen.blit(survival_text, survival_rect)
        screen.blit(training_text, training_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "survival"
                if event.key == pygame.K_2:
                    return "training"

def choose_training_level(): #Chọn training level
    global DIFFICULTY, change_position_interval
    font = pygame.font.SysFont('Comic Sans MS', 30)
    running = True
    round_number = 0

    while running:
        screen.fill(WHITE)
        title_text = font.render("Choose Difficulty", True, BLACK)
        easy_text = font.render("1. Easy", True, BLACK)
        medium_text = font.render("2. Medium", True, BLACK)
        hard_text = font.render("3. Hard", True, BLACK)

        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        easy_rect = easy_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        medium_rect = medium_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        hard_rect = hard_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        screen.blit(title_text, title_rect)
        screen.blit(easy_text, easy_rect)
        screen.blit(medium_text, medium_rect)
        screen.blit(hard_text, hard_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    DIFFICULTY = "easy"
                    running = False
                if event.key == pygame.K_2:
                    DIFFICULTY = "medium"
                    running = False
                elif event.key == pygame.K_3:
                    DIFFICULTY = "hard"
                    running = False

    change_position_interval = difficulty_intervals[DIFFICULTY]
    round_number += 1

# Hàm tính toán hướng đạn
def calculate_bullet_direction(boss_pos, player_pos):
    dx = player_pos[0] - boss_pos[0]
    dy = player_pos[1] - boss_pos[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    return dx / distance, dy / distance

# Hàm xử lý đạn
class Bullet:
    def __init__(self, x, y, direction):
        self.rect = bullet_img.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 10

    def move(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

    def draw(self):
        screen.blit(bullet_img, self.rect)

# Hàm sinh đạn
def spawn_bullets():
    global last_bullet_time
    if time.time() - last_bullet_time >= 1:
        direction = calculate_bullet_direction(player2.center, player1.center)
        bullets.append(Bullet(player2.centerx, player2.centery, direction))
        last_bullet_time = time.time()

# Hàm xử lý va chạm
def handle_bullets():
    global player1_health
    for bullet in bullets[:]:
        bullet.move()
        if player1.colliderect(bullet.rect):
            player1_health -= 5
            bullets.remove(bullet)
        elif bullet.rect.x < 0 or bullet.rect.x > WIDTH or bullet.rect.y < 0 or bullet.rect.y > HEIGHT:
            bullets.remove(bullet)

def survival_mode(): #Chế độ Survival
    global player1_health, player1, current_interval, round_number, bullets, player2, player2_health
    font = pygame.font.SysFont('Comic Sans MS', 30)
    # Thời gian thay đổi vị trí ban đầu
    current_interval = 5
    round_number = 1  # Số vòng đấu
    is_boss = False
    bullets.clear()  # Xóa tất cả đạn khi bắt đầu chế độ survival

    while player1_health > 0:
        player2_health = 100 if not is_boss else 150
        player2.center = (random.randint(150, WIDTH - 150), random.randint(150, HEIGHT - 150))
        last_position_change = time.time()

        while player2_health > 0 and player1_health > 0:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Lấy frame từ webcam
            ret, frame = cap.read()
            if not ret:
                print("Không thể lấy video từ webcam.")
                return

            # Nhận diện cử chỉ tay
            gesture, landmarks = detect_hand_gestures(frame)

            # Di chuyển player1 theo vị trí cổ tay nếu không phải "Rock"
            if landmarks:
                wrist_x = int(landmarks[0].x * WIDTH)
                wrist_y = int(landmarks[0].y * HEIGHT)
                player1.center = (wrist_x, wrist_y)

            # Cập nhật cử chỉ tay
            if gesture == "Rock":
                if player1.colliderect(player2):
                    player2_health -= random.randint(5, 15)
                    player2.center = (random.randint(150, WIDTH - 150), random.randint(150, HEIGHT - 150))
                    last_position_change = time.time()

            # Kiểm tra nếu thời gian đổi vị trí của player2 đã hết
            if time.time() - last_position_change >= current_interval:
                player2.center = (random.randint(150, WIDTH - 150), random.randint(150, HEIGHT - 150))
                player1_health -= random.randint(5, 15)
                last_position_change = time.time()

            # Vẽ các đối tượng lên màn hình
            screen.blit(player1_img, player1.topleft)
            if is_boss:
                screen.blit(boss_img, player2.topleft)
                for bullet in bullets:
                    bullet.draw()

                handle_bullets()
                spawn_bullets()
            else:
                screen.blit(player2_img, player2.topleft)

            # Vẽ thanh máu
            pygame.draw.rect(screen, RED, (50, 50, player1_health * 2, 20))
            pygame.draw.rect(screen, BLUE, (WIDTH - 250, 50, player2_health * 2, 20))

            # Hiển thị số máu
            font = pygame.font.SysFont(None, 25)
            player1_health_text = font.render(f"Health: {player1_health}", True, BLACK)
            player2_health_text = font.render(f"Health: {player2_health}", True, BLACK)
            screen.blit(player1_health_text, (50, 80))
            screen.blit(player2_health_text, (WIDTH - 150, 80))

            pygame.display.flip()
            clock.tick(FPS)

        if player2_health <= 0:
            if is_boss:
                print("You defeated the Boss!")
            else:
                print(f"Round {round_number} cleared!")
            
            round_number += 1
            if round_number % 3 == 0:  # Cứ sau 2 vòng đấu với lính sẽ gặp boss
                is_boss = True
                current_interval = max(0.5, current_interval - 1)
                # Vẽ và xử lý đạn
            else:
                is_boss = False
                current_interval = max(1, current_interval - 0.5)

def show_game_over(winner, mode): #Kết thúc trò chơi
    font = pygame.font.SysFont('Comic Sans MS', 30)
    lose_text = font.render(f"Game Over! {winner} Wins!", True, BLACK)
    exit_text = font.render("Exiting in", True, BLACK)
    
    screen.fill(WHITE)
    screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2))

    if mode == "survival":
        text = font.render(f"Score: {round_number - 1}", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
        screen.blit(text, text_rect)

        for remaining_time in range(countdown_time, 0, -1):
            screen.fill(WHITE)
            
            screen.blit(text, text_rect)
            screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2))
            
            countdown_text = font.render(f"{remaining_time} seconds...", True, BLACK)
            screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 + 50))

            pygame.display.flip()
            pygame.time.delay(1000)  # Chờ 1 giây

    countdown_time = 2  # Đếm ngược trong 2 giây
    for remaining_time in range(countdown_time, 0, -1):
        screen.fill(WHITE)
        screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2))
        
        countdown_text = font.render(f"{remaining_time} seconds...", True, BLACK)
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        pygame.time.delay(1000)  # Chờ 1 giây

    pygame.quit()
    exit()                

def main(mode):
    global player1_health, player2_health, last_position_change_time, player2_last_position_change
    running = True
    font = pygame.font.SysFont(None, 25)

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ret, frame = cap.read()
        if not ret:
            print("Không thể lấy video từ webcam.")
            break

        gesture, landmarks = detect_hand_gestures(frame)

        if landmarks:
            wrist_x = int(landmarks[0].x * WIDTH)
            wrist_y = int(landmarks[0].y * HEIGHT)
            player1.center = (wrist_x, wrist_y)

        if gesture == "Rock":
            if player1.colliderect(player2):
                player2_health -= random.randint(5, 15)
                player2.center = (random.randint(150, WIDTH - 150), random.randint(150, HEIGHT - 150))
                player2_last_position_change = time.time()

        if time.time() - player2_last_position_change >= change_position_interval:
            player2.center = (random.randint(150, WIDTH - 150), random.randint(150, HEIGHT - 150))
            player1_health -= random.randint(5, 15)
            player2_last_position_change = time.time()

        if player1_health <= 0:
            show_game_over("The computers", mode)  # Pass mode to show_game_over
        if player2_health <= 0:
            show_game_over("You", mode)  # Pass mode to show_game_over

        screen.blit(player1_img, player1.topleft)
        screen.blit(player2_img, player2.topleft)

        pygame.draw.rect(screen, RED, (50, 50, player1_health * 2, 20))
        pygame.draw.rect(screen, BLUE, (WIDTH - 250, 50, player2_health * 2, 20))

        player1_health_text = font.render(f"Health: {player1_health}", True, BLACK)
        player2_health_text = font.render(f"Health: {player2_health}", True, BLACK)
        screen.blit(player1_health_text, (50, 80))
        screen.blit(player2_health_text, (WIDTH - 150, 80))

        pygame.display.flip()
        clock.tick(FPS)

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    show_welcome_screen()
    mode = choose_game_mode()
    if mode == "survival":
        survival_mode()
    if mode == "training":
        choose_training_level()
    
    main(mode)