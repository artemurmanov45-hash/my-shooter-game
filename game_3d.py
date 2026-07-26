from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina(borderless=False)

# ------------------ НАСТРОЙКИ (увеличенные потолки) ------------------
ROOM_SIZE = 40
WALL_HEIGHT = 6.0          # увеличено в 2 раза (было 3.0)
WALL_THICKNESS = 0.2
DOOR_WIDTH = 2.0
DOOR_HEIGHT = 3.0          # увеличена высота дверей
WINDOW_WIDTH = 1.5
WINDOW_HEIGHT = 1.5
WINDOW_Y = 1.8             # фиксированная высота центра окна от пола

# ------------------ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ------------------
def create_window(x, y, z, width=1.5, height=1.5):
    """
    Создаёт окно с рамкой и стеклом.
    Параметры:
        x, y, z – координаты центра окна,
        width, height – ширина и высота стекла (по умолчанию 1.5x1.5).
    """
    # Цвета (кортежи RGBA)
    frame_color = (100, 80, 60, 255)      # коричневая рамка
    glass_color = (150, 200, 255, 100)    # полупрозрачное голубое стекло

    # Стекло
    glass = Entity(
        model='cube',
        color=glass_color,
        scale=(width, height, 0.05),
        position=(x, y, z)
    )

    # Рамка – четыре планки
    # Верхняя планка
    Entity(
        model='cube',
        color=frame_color,
        scale=(width, 0.05, 0.1),
        position=(x, y + height/2, z)
    )
    # Нижняя планка
    Entity(
        model='cube',
        color=frame_color,
        scale=(width, 0.05, 0.1),
        position=(x, y - height/2, z)
    )
    # Левая планка
    Entity(
        model='cube',
        color=frame_color,
        scale=(0.05, height, 0.1),
        position=(x - width/2, y, z)
    )
    # Правая планка
    Entity(
        model='cube',
        color=frame_color,
        scale=(0.05, height, 0.1),
        position=(x + width/2, y, z)
    )
    # Средняя горизонтальная перекладина (для красоты)
    Entity(
        model='cube',
        color=frame_color,
        scale=(width, 0.03, 0.1),
        position=(x, y, z)
    )
    # Рамка
    Entity(model='cube', color=frame_color, scale=(width, 0.05, 0.1), position=(x, y + height/2, z))
    Entity(model='cube', color=frame_color, scale=(width, 0.05, 0.1), position=(x, y - height/2, z))
    Entity(model='cube', color=frame_color, scale=(0.05, height, 0.1), position=(x - width/2, y, z))
    Entity(model='cube', color=frame_color, scale=(0.05, height, 0.1), position=(x + width/2, y, z))
    Entity(model='cube', color=frame_color, scale=(width, 0.03, 0.1), position=(x, y, z))
    return glass

def create_room(x_offset, z_offset,
                has_left_door=False, has_right_door=False,
                has_front_door=False, has_back_door=False,
                has_window_left=False, has_window_right=False,
                has_window_front=False, has_window_back=False,
                floor_texture='dark_wood', wall_texture='ceiling.png'):
    half = ROOM_SIZE / 2
    y_center = WALL_HEIGHT / 2

    # Пол – теперь серый
    floor = Entity(
        model='cube',
        texture=floor_texture,
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, -0.05, z_offset),
        collider='box',
        color=color.gray            # <-- изменено на серый
    )

    # Потолок – теперь серый
    ceiling = Entity(
        model='cube',
        texture='tile',
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, WALL_HEIGHT, z_offset),
        color=color.gray            # <-- изменено на серый (было (40,40,40,255))
    )

    # Стены – с увеличенной детализацией текстур (texture_scale)
    # Задняя (Z-)
    wall_z_neg = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),        # повтор текстуры 8x8 для мелкого кирпича
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset - half),
        collider='box'
    )
    # Передняя (Z+)
    wall_z_pos = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset + half),
        collider='box'
    )
    # Левая (X-)
    wall_x_neg = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset - half, y_center, z_offset),
        collider='box'
    )
    # Правая (X+)
    wall_x_pos = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset + half, y_center, z_offset),
        collider='box'
    )

    # ---- ДВЕРНЫЕ ПРОЁМЫ (увеличенной высоты) ----
    if has_left_door:
        destroy(wall_x_neg)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        # Левая часть стены
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
            position=(x_offset - half, y_center, z_offset - half_door/2),
            collider='box'
        )
        # Правая часть стены
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
            position=(x_offset - half, y_center, z_offset + half_door/2),
            collider='box'
        )
        # Верхняя часть над дверью (перемычка) – теперь она выше
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
            position=(x_offset - half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset),
            collider='box'
        )
    if has_right_door:
        destroy(wall_x_pos)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
            position=(x_offset + half, y_center, z_offset - half_door/2),
            collider='box'
        )
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
            position=(x_offset + half, y_center, z_offset + half_door/2),
            collider='box'
        )
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
            position=(x_offset + half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset),
            collider='box'
        )

    # Двери на передней и задней стенах
    if has_front_door:
        destroy(wall_z_pos)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
            position=(x_offset - half_door/2, y_center, z_offset + half),
            collider='box'
        )
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
            position=(x_offset + half_door/2, y_center, z_offset + half),
            collider='box'
        )
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(DOOR_WIDTH, WALL_HEIGHT - DOOR_HEIGHT, WALL_THICKNESS),
            position=(x_offset, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset + half),
            collider='box'
        )
    if has_back_door:
        destroy(wall_z_neg)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
            position=(x_offset - half_door/2, y_center, z_offset - half),
            collider='box'
        )
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
            position=(x_offset + half_door/2, y_center, z_offset - half),
            collider='box'
        )
        Entity(
            model='cube',
            texture=wall_texture,
            texture_scale=(8, 8),
            scale=(DOOR_WIDTH, WALL_HEIGHT - DOOR_HEIGHT, WALL_THICKNESS),
            position=(x_offset, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset - half),
            collider='box'
        )

    # ---- ОКНА (на фиксированной высоте) ----
    if has_window_back:
        for i in range(-1, 2):
            create_window(x_offset + i*3, WINDOW_Y, z_offset - half - 0.1)
    if has_window_front:
        for i in range(-1, 2):
            create_window(x_offset + i*3, WINDOW_Y, z_offset + half + 0.1)
    if has_window_left and not has_left_door:
        for i in range(-1, 2):
            create_window(x_offset - half - 0.1, WINDOW_Y, z_offset + i*3)
    if has_window_right and not has_right_door:
        for i in range(-1, 2):
            create_window(x_offset + half + 0.1, WINDOW_Y, z_offset + i*3)

    # ---- ОСВЕЩЕНИЕ (поднято под потолок) ----
    light = PointLight(
        position=(x_offset, WALL_HEIGHT - 0.3, z_offset),
        color=color.rgb(255, 240, 200),
        intensity=2.0,
        range=30
    )
    lamp = Entity(
        model='cube',
        color=color.rgb(200, 200, 200),
        scale=(0.3, 0.1, 0.3),
        position=(x_offset, WALL_HEIGHT - 0.1, z_offset)
    )

# ---- СОЗДАНИЕ СЕТКИ КОМНАТ (квадратный периметр) ----
grid_size = 3  # 3x3 = 9 комнат (можно увеличить)
# Вычисляем сдвиг, чтобы центр сетки оказался в (0,0)
offset_x = -(grid_size - 1) * ROOM_SIZE / 2
offset_z = -(grid_size - 1) * ROOM_SIZE / 2

# Соберём центры всех комнат для использования во врагах
room_centers = []

# Полный путь к текстуре пола
floor_texture_path = r'C:\Users\123398\Desktop\Разработка\Game\ceiling.png'

for ix in range(grid_size):
    for iz in range(grid_size):
        x = ix * ROOM_SIZE + offset_x
        z = iz * ROOM_SIZE + offset_z
        room_centers.append((x, z))

        # Определяем наличие дверей по соседям
        has_left = (ix > 0)
        has_right = (ix < grid_size - 1)
        has_front = (iz < grid_size - 1)  # Z+
        has_back = (iz > 0)               # Z-

        # Окна только на внешних стенах, где нет дверей
        win_left = (ix == 0)
        win_right = (ix == grid_size - 1)
        win_front = (iz == grid_size - 1)
        win_back = (iz == 0)

        create_room(x, z,
                    has_left_door=has_left,
                    has_right_door=has_right,
                    has_front_door=has_front,
                    has_back_door=has_back,
                    has_window_left=win_left,
                    has_window_right=win_right,
                    has_window_front=win_front,
                    has_window_back=win_back,
                    floor_texture=floor_texture_path,
                    wall_texture='brick')

# ---- ДВЕРНЫЕ РАМЫ (декоративные) для всех проёмов ----
for ix in range(grid_size):
    for iz in range(grid_size):
        x = ix * ROOM_SIZE + offset_x
        z = iz * ROOM_SIZE + offset_z
        # Горизонтальные рамы (между комнатами по X)
        if ix < grid_size - 1:
            Entity(
                model='cube',
                color=color.rgb(100, 80, 60),
                scale=(0.1, DOOR_HEIGHT, DOOR_WIDTH + 0.2),
                position=(x + ROOM_SIZE/2, DOOR_HEIGHT/2, z)
            )
        # Вертикальные рамы (между комнатами по Z)
        if iz < grid_size - 1:
            Entity(
                model='cube',
                color=color.rgb(100, 80, 60),
                scale=(DOOR_WIDTH + 0.2, DOOR_HEIGHT, 0.1),
                position=(x, DOOR_HEIGHT/2, z + ROOM_SIZE/2)
            )

# ---- ИГРОК (перемещён в центр) ----
player = FirstPersonController()
player.position = (0, 1, 0)   # теперь старт в центральной комнате
base_speed = 10                # обычная скорость ходьбы

# ---- ОРУЖИЕ ----
gun = Entity(
    parent=camera,
    model='cube',
    color=color.dark_gray,
    scale=(0.2, 0.1, 0.5),
    position=(0.3, -0.2, 0.5)
)
barrel = Entity(
    parent=gun,
    model='cube',
    color=color.black,
    scale=(0.1, 0.08, 0.2),
    position=(0, 0, 0.35)
)
grip = Entity(
    parent=gun,
    model='cube',
    color=color.brown,
    scale=(0.12, 0.2, 0.1),
    position=(0, -0.15, -0.1)
)

# ---- ВРАГИ (по 4 на комнату) ----
enemies = []
def create_enemy():
    if room_centers:
        cx, cz = random.choice(room_centers)
        x = cx + random.uniform(-18, 18)
        z = cz + random.uniform(-18, 18)
        enemy = Entity(model='sphere', color=color.black, scale=0.5, position=(x, 0.5, z))
        enemies.append(enemy)

for _ in range(grid_size * grid_size * 4):
    create_enemy()

score = 0
score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2)

# ---- СПИСОК АКТИВНЫХ ПУЛЬ ----
bullets = []

def create_bullet():
    # Создаём пулю
    start_pos = player.position + player.forward * 0.8 + Vec3(0, 0.2, 0)
    bullet = Entity(
        model='cube',
        color=color.yellow,
        scale=(0.05, 0.05, 0.2),
        position=start_pos,
        rotation=player.rotation
    )
    # Свечение
    Entity(
        parent=bullet,
        model='sphere',
        color=color.white,
        scale=(0.1, 0.1, 0.1)
    )
    bullet.velocity = player.forward * 30
    bullet.lifetime = 1.0   # живёт 1 секунду, если не попала
    bullets.append(bullet)

def spawn_explosion(pos):
    # Эффект взрыва
    for _ in range(10):
        p = Entity(
            model='cube',
            color=color.red,
            scale=0.1,
            position=pos,
            rotation=random.random() * 360
        )
        p.velocity = (
            Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)).normalized()
            * random.uniform(3, 6)
        )
        destroy(p, delay=0.3)
    # Звук попадания (если файла нет, ошибки не будет)
    try:
        Audio('shot_echo', loop=False, autoplay=True)
    except:
        pass

def update():
    global score
    # ---- БЕГ (ускорение при зажатом Shift) ----
    if held_keys['shift']:
        player.speed = base_speed * 3   # в 3 раза быстрее
    else:
        player.speed = base_speed

    # ---- ДВИЖЕНИЕ ПУЛЬ И ПРОВЕРКА ПОПАДАНИЙ ----
    for bullet in bullets[:]:
        bullet.position += bullet.velocity * time.dt
        bullet.lifetime -= time.dt
        hit = False
        for enemy in enemies[:]:
            if distance(bullet.position, enemy.position) < 0.8:
                spawn_explosion(enemy.position)
                destroy(enemy)
                enemies.remove(enemy)
                create_enemy()
                score += 1
                hit = True
                break
        if hit or bullet.lifetime <= 0:
            destroy(bullet)
            bullets.remove(bullet)

    # ---- ДВИЖЕНИЕ ВРАГОВ ----
    for enemy in enemies[:]:
        dir = (player.position - enemy.position)
        dir.y = 0
        if dir.length() > 0.5:
            enemy.position += dir.normalized() * time.dt * 1.5
        if distance(enemy.position, player.position) < 1.5:
            destroy(enemy)
            enemies.remove(enemy)
            create_enemy()
    score_text.text = f'Score: {score}'

def input(key):
    global score
    if key == 'left mouse down':
        # Отдача оружия
        gun.position = (0.3, -0.2, 0.3)
        invoke(setattr, gun, 'position', (0.3, -0.2, 0.5), delay=0.1)

        create_bullet()
    if key == 'escape':
        app.quit()

# Глобальное освещение
AmbientLight(color=color.rgba(50, 50, 50, 0.3))

app.run()