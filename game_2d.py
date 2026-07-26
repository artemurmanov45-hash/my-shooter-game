import pygame
import math
import random

# Инициализация Pygame (окно будет создано в main.py, но здесь мы тоже можем создать,
# но для единообразия создадим своё окно в функции play_2d)

def draw_player(surface, pos, color, shape, radius):
    """Рисует игрока заданной формы и цвета."""
    if shape == 'circle':
        pygame.draw.circle(surface, color, (int(pos[0]), int(pos[1])), radius)
    elif shape == 'square':
        rect = pygame.Rect(pos[0]-radius, pos[1]-radius, radius*2, radius*2)
        pygame.draw.rect(surface, color, rect)
    elif shape == 'triangle':
        points = [(pos[0], pos[1]-radius),
                  (pos[0]-radius, pos[1]+radius),
                  (pos[0]+radius, pos[1]+radius)]
        pygame.draw.polygon(surface, color, points)

def play_2d(player_color, player_shape):
    """Запускает 2D-игру с заданными цветом и формой игрока."""
    # Инициализация (если окно уже создано, используем его, но для простоты создаём своё)
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Шутер")
    clock = pygame.time.Clock()

    # Цвета
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)

    # Параметры игрока
    player_radius = 15
    player_speed = 4
    player_health = 100
    player_pos = [WIDTH // 2, HEIGHT // 2]

    # Список пуль
    bullets = []
    bullet_speed = 10
    bullet_radius = 5
    fire_cooldown = 0
    fire_delay = 10

    # Список ботов
    bots = []
    bot_radius = 15
    bot_spawn_timer = 0
    bot_spawn_delay = 60
    max_bots = 10

    font = pygame.font.Font(None, 36)

    def spawn_bot():
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = -bot_radius
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT + bot_radius
        elif side == 'left':
            x = -bot_radius
            y = random.randint(0, HEIGHT)
        else:
            x = WIDTH + bot_radius
            y = random.randint(0, HEIGHT)
        bots.append({
            'pos': [x, y],
            'health': 1,
            'speed': random.uniform(1.0, 2.0)
        })

    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if fire_cooldown <= 0:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dx = mouse_x - player_pos[0]
                    dy = mouse_y - player_pos[1]
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        dx /= dist
                        dy /= dist
                    bullets.append({
                        'pos': player_pos.copy(),
                        'vel': [dx * bullet_speed, dy * bullet_speed]
                    })
                    fire_cooldown = fire_delay

        # Движение игрока
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_pos[0] += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_pos[1] += player_speed

        player_pos[0] = max(player_radius, min(WIDTH - player_radius, player_pos[0]))
        player_pos[1] = max(player_radius, min(HEIGHT - player_radius, player_pos[1]))

        # Перемещение пуль
        for bullet in bullets[:]:
            bullet['pos'][0] += bullet['vel'][0]
            bullet['pos'][1] += bullet['vel'][1]
            if (bullet['pos'][0] < 0 or bullet['pos'][0] > WIDTH or
                bullet['pos'][1] < 0 or bullet['pos'][1] > HEIGHT):
                bullets.remove(bullet)

        # Перемещение ботов
        for bot in bots[:]:
            dx = player_pos[0] - bot['pos'][0]
            dy = player_pos[1] - bot['pos'][1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                bot['pos'][0] += (dx / dist) * bot['speed']
                bot['pos'][1] += (dy / dist) * bot['speed']

        # Столкновения пуль с ботами
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet['pos'][0] - bullet_radius,
                                      bullet['pos'][1] - bullet_radius,
                                      bullet_radius * 2, bullet_radius * 2)
            for bot in bots[:]:
                bot_rect = pygame.Rect(bot['pos'][0] - bot_radius,
                                       bot['pos'][1] - bot_radius,
                                       bot_radius * 2, bot_radius * 2)
                if bullet_rect.colliderect(bot_rect):
                    bots.remove(bot)
                    bullets.remove(bullet)
                    break

        # Столкновения ботов с игроком
        player_rect = pygame.Rect(player_pos[0] - player_radius,
                                  player_pos[1] - player_radius,
                                  player_radius * 2, player_radius * 2)
        for bot in bots[:]:
            bot_rect = pygame.Rect(bot['pos'][0] - bot_radius,
                                   bot['pos'][1] - bot_radius,
                                   bot_radius * 2, bot_radius * 2)
            if player_rect.colliderect(bot_rect):
                player_health -= 10
                bots.remove(bot)
                if player_health <= 0:
                    running = False  # выход из игры – возврат в меню

        # Спавн ботов
        if len(bots) < max_bots:
            bot_spawn_timer += 1
            if bot_spawn_timer >= bot_spawn_delay:
                spawn_bot()
                bot_spawn_timer = 0

        if fire_cooldown > 0:
            fire_cooldown -= 1

        # Отрисовка
        screen.fill(BLACK)

        # Игрок (используем переданные цвет и форму)
        draw_player(screen, player_pos, player_color, player_shape, player_radius)

        # Прицельная линия
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(screen, YELLOW, player_pos, (mouse_x, mouse_y), 2)

        # Пули
        for bullet in bullets:
            pygame.draw.circle(screen, WHITE, (int(bullet['pos'][0]), int(bullet['pos'][1])), bullet_radius)

        # Боты
        for bot in bots:
            pygame.draw.circle(screen, RED, (int(bot['pos'][0]), int(bot['pos'][1])), bot_radius)

        # Здоровье
        health_text = font.render(f"HP: {player_health}", True, WHITE)
        screen.blit(health_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # После завершения игрового цикла закрываем окно и возвращаемся в меню
    pygame.quit()