from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina(borderless=False)

# ------------------ НАСТРОЙКИ ------------------
# Размеры комнат (в метрах)
ROOM_SIZE = 4
WALL_HEIGHT = 2.5
WALL_THICKNESS = 0.2

# Цвета/текстуры
wall_texture = 'brick'   # встроенная текстура кирпича
floor_texture = 'wood'   # текстура дерева
ceiling_texture = 'white_cube'

# ------------------ ПОСТРОЕНИЕ КОМНАТ ------------------
def create_room(x_offset, z_offset, has_door=False, door_side='right'):
    """
    Создаёт комнату размером ROOM_SIZE x ROOM_SIZE с центром в (x_offset, 0, z_offset).
    if has_door: создаёт дверной проём на указанной стене (door_side: 'right' или 'left').
    """
    half = ROOM_SIZE / 2
    y_center = WALL_HEIGHT / 2

    # Пол
    floor = Entity(
        model='cube',
        texture=floor_texture,
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, -0.05, z_offset),
        collider='box'
    )

    # Потолок (можно без коллизий)
    ceiling = Entity(
        model='cube',
        texture=ceiling_texture,
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, WALL_HEIGHT, z_offset)
    )

    # Стены (четыре стены, каждая - куб)
    # Стена 1: задняя (Z = z_offset - half)
    wall_z_neg = Entity(
        model='cube',
        texture=wall_texture,
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset - half),
        collider='box'
    )
    # Стена 2: передняя (Z = z_offset + half)
    wall_z_pos = Entity(
        model='cube',
        texture=wall_texture,
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset + half),
        collider='box'
    )
    # Стена 3: левая (X = x_offset - half)
    wall_x_neg = Entity(
        model='cube',
        texture=wall_texture,
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset - half, y_center, z_offset),
        collider='box'
    )
    # Стена 4: правая (X = x_offset + half)
    wall_x_pos = Entity(
        model='cube',
        texture=wall_texture,
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset + half, y_center, z_offset),
        collider='box'
    )

    # Если нужна дверь - убираем часть стены (создаём проём)
    if has_door:
        door_width = 1.0
        door_height = 2.0
        # Определяем, на какой стене делать дверь
        if door_side == 'right':
            # Правая стена (x_offset + half). Удаляем её и создаём две половинки
            destroy(wall_x_pos)
            # Левая половинка двери (от x_offset+half - ROOM_SIZE/2 до x_offset+half - door_width/2)
            half_door = (ROOM_SIZE - door_width) / 2
            # Левая часть стены
            wall_left_door = Entity(
                model='cube',
                texture=wall_texture,
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset + half, y_center, z_offset - half_door/2),
                collider='box'
            )
            # Правая часть стены
            wall_right_door = Entity(
                model='cube',
                texture=wall_texture,
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset + half, y_center, z_offset + half_door/2),
                collider='box'
            )
            # Верхняя часть над дверью (перемычка)
            lintel = Entity(
                model='cube',
                texture=wall_texture,
                scale=(WALL_THICKNESS, WALL_HEIGHT - door_height, door_width),
                position=(x_offset + half, (WALL_HEIGHT - door_height)/2 + door_height, z_offset),
                collider='box'
            )
        elif door_side == 'left':
            # Левая стена (x_offset - half)
            destroy(wall_x_neg)
            half_door = (ROOM_SIZE - door_width) / 2
            wall_left_door = Entity(
                model='cube',
                texture=wall_texture,
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset - half, y_center, z_offset - half_door/2),
                collider='box'
            )
            wall_right_door = Entity(
                model='cube',
                texture=wall_texture,
                scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
                position=(x_offset - half, y_center, z_offset + half_door/2),
                collider='box'
            )
            lintel = Entity(
                model='cube',
                texture=wall_texture,
                scale=(WALL_THICKNESS, WALL_HEIGHT - door_height, door_width),
                position=(x_offset - half, (WALL_HEIGHT - door_height)/2 + door_height, z_offset),
                collider='box'
            )
        # Можно также сделать дверь на передней/задней стене, но для двух комнат достаточно правой/левой.

# Создаём две комнаты: левую (x=-2.5) и правую (x=2.5), между ними дверь на правой стене левой комнаты и на левой стене правой комнаты.
# Но чтобы дверь была одна общая, сделаем так: левая комната имеет дверь на правой стене, правая комната имеет дверь на левой стене.
# При этом стена между комнатами будет общей, и дверной проём будет сквозным.

# Левая комната (центр в x = -2.5, z = 0) с дверью на правой стене
create_room(-2.5, 0, has_door=True, door_side='right')
# Правая комната (центр в x = 2.5, z = 0) с дверью на левой стене
create_room(2.5, 0, has_door=True, door_side='left')

# Чтобы дверной проём был проходимым, мы уже удалили центральные стены. 
# Но между комнатами остаётся небольшой зазор? Нет, потому что мы создаём отдельные стены, но они не перекрывают друг друга.
# Для лучшего эффекта можно добавить дверную раму (коробку) - просто декоративные элементы.

# Добавим простую дверную раму (опционально)
door_frame_color = color.rgb(100, 80, 60)
frame = Entity(
    model='cube',
    color=door_frame_color,
    scale=(0.1, WALL_HEIGHT, 1.2),
    position=(0, WALL_HEIGHT/2, 0)   # центр между комнатами
)
# Вертикальные стойки рамы можно сделать, но для простоты оставим.

# ------------------ ИГРОК ------------------
player = FirstPersonController()
player.position = (-1.5, 1, 0)  # внутри левой комнаты

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

# ------------------ ВРАГИ (для интереса) ------------------
enemies = []
def create_enemy():
    # Спавним врагов в правой комнате
    x = random.uniform(1.5, 3.5)
    z = random.uniform(-1.5, 1.5)
    enemy = Entity(model='sphere', color=color.red, scale=0.5, position=(x, 0.5, z))
    enemies.append(enemy)

for _ in range(3):
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
        # Отдача
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

# ------------------ ОСВЕЩЕНИЕ ------------------
# Добавим свет, чтобы было видно текстуры
pivot = Entity()
DirectionalLight(parent=pivot, y=2, z=3, rotation=(45, -45, 0))
AmbientLight(color=color.rgba(100,100,100,0.5))

app.run()