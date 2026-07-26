from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina(borderless=False)

# ------------------ НАСТРОЙКИ ------------------
# Размеры комнат (в метрах) - увеличены в 10 раз
ROOM_SIZE = 40
WALL_HEIGHT = 10          # высота стен (было 2.5)
WALL_THICKNESS = 0.4      # чуть толще

# Для дверного проёма (увеличим пропорционально)
DOOR_WIDTH = 2.5
DOOR_HEIGHT = 5.0

# ------------------ ПОСТРОЕНИЕ КОМНАТ ------------------
def create_room(x_offset, z_offset, has_door=False, door_side='right'):
    half = ROOM_SIZE / 2
    y_center = WALL_HEIGHT / 2

    # Пол
    floor = Entity(
        model='cube',
        texture='wood',
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, -0.05, z_offset),
        collider='box'
    )

    # Потолок
    ceiling = Entity(
        model='cube',
        texture='white_cube',
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, WALL_HEIGHT, z_offset)
    )

    # Стены
    # Задняя (Z = z_offset - half)
    wall_z_neg = Entity(
        model='cube',
        texture='brick',
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset - half),
        collider='box'
    )
    # Передняя (Z = z_offset + half)
    wall_z_pos = Entity(
        model='cube',
        texture='brick',
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset + half),
        collider='box'
    )
    # Левая (X = x_offset - half)
    wall_x_neg = Entity(
        model='cube',
        texture='brick',
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset - half, y_center, z_offset),
        collider='box'
    )
    # Правая (X = x_offset + half) - может быть заменена на дверь
    wall_x_pos = Entity(
        model='cube',
        texture='brick',
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset + half, y_center, z_offset),
        collider='box'
    )

    if has_door:
        # Удаляем целую стену, затем создаём части с проёмом
        # Определяем, на какой стене делать дверь
        if door_side == 'right':
            destroy(wall_x_pos)
            half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
            # Левая часть стены (от центра стены влево)
            wall_left_door = Entity(
                model='cube',
                texture='brick',
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset + half, y_center, z_offset - half_door/2),
                collider='box'
            )
            # Правая часть стены
            wall_right_door = Entity(
                model='cube',
                texture='brick',
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset + half, y_center, z_offset + half_door/2),
                collider='box'
            )
            # Перемычка над дверью
            lintel = Entity(
                model='cube',
                texture='brick',
                scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
                position=(x_offset + half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset),
                collider='box'
            )
        elif door_side == 'left':
            destroy(wall_x_neg)
            half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
            wall_left_door = Entity(
                model='cube',
                texture='brick',
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset - half, y_center, z_offset - half_door/2),
                collider='box'
            )
            wall_right_door = Entity(
                model='cube',
                texture='brick',
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset - half, y_center, z_offset + half_door/2),
                collider='box'
            )
            lintel = Entity(
                model='cube',
                texture='brick',
                scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
                position=(x_offset - half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset),
                collider='box'
            )

# Создаём две комнаты: левая (x = -25) и правая (x = 25), между ними дверь
create_room(-25, 0, has_door=True, door_side='right')
create_room(25, 0, has_door=True, door_side='left')

# Декоративная дверная рама (между комнатами)
door_frame_color = color.rgb(100, 80, 60)
frame = Entity(
    model='cube',
    color=door_frame_color,
    scale=(0.1, WALL_HEIGHT, DOOR_WIDTH + 0.4),
    position=(0, WALL_HEIGHT/2, 0)
)

# ------------------ ИГРОК ------------------
player = FirstPersonController()
player.position = (-15, 2, 0)  # внутри левой комнаты, не у стены

# ------------------ ОРУЖИЕ (пистолет) ------------------
gun = Entity(
    parent=camera,
    model='cube',
    color=color.dark_gray,
    scale=(0.2, 0.1, 0.5),
    position=(0.3, -0.2, 0.5),
    rotation=(0, 0, 0)
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

# ------------------ ВРАГИ (красные шары) ------------------
enemies = []
def create_enemy():
    # Спавним врагов в правой комнате (от 15 до 35 по X, Z в пределах -15..15)
    x = random.uniform(15, 35)
    z = random.uniform(-15, 15)
    enemy = Entity(model='sphere', color=color.red, scale=0.7, position=(x, 0.5, z))
    enemies.append(enemy)

for _ in range(8):  # больше врагов для большой карты
    create_enemy()

score = 0
score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2)

def update():
    global score
    for enemy in enemies[:]:
        dir = (player.position - enemy.position)
        dir.y = 0
        if dir.length() > 0.5:
            enemy.position += dir.normalized() * time.dt * 2.0  # чуть быстрее
        if distance(enemy.position, player.position) < 2.0:  # увеличен радиус касания
            destroy(enemy)
            enemies.remove(enemy)
            create_enemy()
    score_text.text = f'Score: {score}'

def input(key):
    global score
    if key == 'left mouse down':
        # Отдача
        gun.position = (0.3, -0.2, 0.3)
        invoke(setattr, gun, 'position', (0.3, -0.2, 0.5), delay=0.1)

        bullet = Entity(model='sphere', color=color.yellow, scale=0.1, position=player.position + player.forward*0.5)
        bullet.velocity = player.forward * 40  # пуля быстрее
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

# ------------------ ОСВЕЩЕНИЕ ------------------
pivot = Entity()
DirectionalLight(parent=pivot, y=5, z=10, rotation=(45, -45, 0))
AmbientLight(color=color.rgba(100,100,100,0.5))

app.run()