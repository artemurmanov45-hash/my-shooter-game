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
def create_window(x, y, z, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
    """Создаёт окно с рамкой и стеклом."""
    frame_color = color.rgb(100, 80, 60)
    # Стекло
    glass = Entity(
        model='cube',
        color=color.rgba(150, 200, 255, 100),
        scale=(width, height, 0.05),
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
                has_window_left=False, has_window_right=False,
                has_window_front=False, has_window_back=False,
                floor_texture='dark_wood', wall_texture='brick'):
    half = ROOM_SIZE / 2
    y_center = WALL_HEIGHT / 2

    # Пол (тёмный)
    floor = Entity(
        model='cube',
        texture=floor_texture,
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, -0.05, z_offset),
        collider='box',
        color=color.rgb(60, 40, 30)
    )

    # Потолок (светлая плитка)
    ceiling = Entity(
        model='cube',
        texture='tile',
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, WALL_HEIGHT, z_offset),
        color=color.rgb(230, 230, 230)
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

# ---- СОЗДАНИЕ ТРЁХ КОМНАТ ----
create_room(-40, 0,
            has_right_door=True,
            has_window_left=True,
            has_window_front=True,
            has_window_back=True,
            floor_texture='dark_wood', wall_texture='brick')

create_room(0, 0,
            has_left_door=True,
            has_right_door=True,
            has_window_front=True,
            has_window_back=True,
            floor_texture='dark_wood', wall_texture='brick')

create_room(40, 0,
            has_left_door=True,
            has_window_right=True,
            has_window_front=True,
            has_window_back=True,
            floor_texture='dark_wood', wall_texture='brick')

# Дверные рамы (декоративные, теперь выше)
frame1 = Entity(
    model='cube',
    color=color.rgb(100, 80, 60),
    scale=(0.1, DOOR_HEIGHT, DOOR_WIDTH + 0.2),
    position=(-20, DOOR_HEIGHT/2, 0)
)
frame2 = Entity(
    model='cube',
    color=color.rgb(100, 80, 60),
    scale=(0.1, DOOR_HEIGHT, DOOR_WIDTH + 0.2),
    position=(20, DOOR_HEIGHT/2, 0)
)

# ---- ИГРОК ----
player = FirstPersonController()
player.position = (-30, 1, 0)

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

# ---- ВРАГИ (20 штук) ----
enemies = []
def create_enemy():
    room = random.choice(['left', 'center', 'right'])
    if room == 'left':
        x = random.uniform(-35, -5)
    elif room == 'center':
        x = random.uniform(-18, 18)
    else:
        x = random.uniform(5, 35)
    z = random.uniform(-18, 18)
    enemy = Entity(model='sphere', color=color.red, scale=0.5, position=(x, 0.5, z))
    enemies.append(enemy)

for _ in range(20):
    create_enemy()

score = 0
score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2)

def update():
    global score
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
        gun.position = (0.3, -0.2, 0.3)
        invoke(setattr, gun, 'position', (0.3, -0.2, 0.5), delay=0.1)

        bullet = Entity(model='sphere', color=color.yellow, scale=0.1, position=player.position + player.forward*0.5)
        bullet.velocity = player.forward * 30
        for enemy in enemies[:]:
            if distance(bullet.position, enemy.position) < 1.0:
                destroy(enemy)
                enemies.remove(enemy)
                score += 1
                create_enemy()
                break
        destroy(bullet, delay=0.5)
    if key == 'escape':
        app.quit()

# Глобальное освещение
AmbientLight(color=color.rgba(50, 50, 50, 0.3))

app.run()