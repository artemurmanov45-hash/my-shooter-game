from ursina import *
from settings import *

building_objects = []

def add_to_building(entity):
    building_objects.append(entity)
    return entity

def create_wall(x, y, z, width, height, depth, color=color.dark_gray, texture=None, collider=True):
    kwargs = {
        'model': 'cube',
        'color': color,
        'scale': (width, height, depth),
        'position': (x, y, z)
    }
    if texture:
        kwargs['texture'] = texture
    if collider:
        kwargs['collider'] = 'box'
    entity = Entity(**kwargs)
    return add_to_building(entity)

def create_door(x, y, z, width=1.5, height=2.5, color=color.lime, texture=None):
    kwargs = {
        'model': 'cube',
        'color': color,
        'scale': (width, height, 0.05),
        'position': (x, y, z),
        'collider': None
    }
    if texture:
        kwargs['texture'] = texture
    entity = Entity(**kwargs)
    return add_to_building(entity)

def create_floor(x, y, z, width, depth, color=color.gray, texture=None):
    thickness = 0.5
    kwargs = {
        'model': 'cube',
        'color': color,
        'scale': (width, thickness, depth),
        'position': (x, y + thickness/2, z),
        'collider': 'box'
    }
    if texture:
        kwargs['texture'] = texture
    entity = Entity(**kwargs)
    return add_to_building(entity)

def create_ceiling(x, y, z, width, depth, color=color.light_gray, texture=None):
    kwargs = {
        'model': 'cube',
        'color': color,
        'scale': (width, 0.2, depth),
        'position': (x, y, z)
    }
    if texture:
        kwargs['texture'] = texture
    entity = Entity(**kwargs)
    return add_to_building(entity)

def generate_grid_rooms():
    """Генерирует сетку комнат с проходами."""
    global building_objects
    building_objects.clear()

    # Параметры из настроек
    rooms_x = GRID_ROOMS_X
    rooms_z = GRID_ROOMS_Z
    room_w = GRID_ROOM_WIDTH
    room_d = GRID_ROOM_DEPTH
    wall_thick = GRID_WALL_THICKNESS
    door_w = GRID_DOOR_WIDTH
    door_h = GRID_DOOR_HEIGHT
    door_prob = GRID_DOOR_PROBABILITY
    height = BIG_ROOM_HEIGHT  # используем высоту из параметров большой комнаты

    # Общий размер всей сетки с учётом стен
    total_width = rooms_x * room_w + (rooms_x + 1) * wall_thick
    total_depth = rooms_z * room_d + (rooms_z + 1) * wall_thick
    half_x = total_width / 2
    half_z = total_depth / 2

    # Пол и потолок – общие для всей зоны
    create_floor(0, 0, 0, total_width, total_depth, color.gray, TEXTURE_FLOOR)
    create_ceiling(0, height, 0, total_width, total_depth, color.light_gray, TEXTURE_CEILING)

    # Создаём сетку комнат
    # Для каждой ячейки (i, j) строим стены, но только те, которые не являются общими с соседней комнатой.
    # Будем строить стены для каждой комнаты: нижнюю (z-), верхнюю (z+), левую (x-), правую (x+)
    # Но чтобы не дублировать, будем строить только правую и верхнюю стены для каждой комнаты,
    # а левую и нижнюю – как левую/нижнюю соседней.
    # Проще: для каждой комнаты построим все 4 стены, но если стена общая, то мы её уже построили, поэтому проверяем.

    # Для хранения центров комнат (для спавна врагов)
    room_centers = []

    # Цикл по комнатам
    for ix in range(rooms_x):
        for iz in range(rooms_z):
            # Координаты центра комнаты
            x_center = -half_x + wall_thick + ix * (room_w + wall_thick) + room_w/2
            z_center = -half_z + wall_thick + iz * (room_d + wall_thick) + room_d/2
            room_centers.append((x_center, z_center))

            # Строим стены для текущей комнаты
            # Левая стена (X = x_center - room_w/2), если ix == 0 или у соседа слева нет проёма
            if ix == 0:
                # внешняя левая стена
                create_wall(x_center - room_w/2 - wall_thick/2, height/2, z_center,
                            wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                # внутренняя стена между текущей и левой комнатой
                # Проверяем, есть ли проход между (ix-1, iz) и (ix, iz)
                if random.random() < door_prob:
                    # Создаём проём (дверь)
                    # Стена разбивается на две части: левую и правую от проёма
                    # Определим позицию проёма по Z (центр стены)
                    door_z = z_center
                    # Левая часть стены (от -room_d/2 до door_z - door_w/2)
                    left_width = room_d/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center - room_w/2 - wall_thick/2, height/2,
                                    z_center - left_width/2,
                                    wall_thick, height, left_width, color.dark_gray, TEXTURE_WALL_INNER)
                    # Правая часть
                    right_width = room_d/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center - room_w/2 - wall_thick/2, height/2,
                                    z_center + right_width/2,
                                    wall_thick, height, right_width, color.dark_gray, TEXTURE_WALL_INNER)
                    # Дверь (визуальный проём)
                    create_door(x_center - room_w/2 - wall_thick/2 - 0.05, door_h/2, z_center,
                                door_w, door_h)
                else:
                    # Сплошная стена
                    create_wall(x_center - room_w/2 - wall_thick/2, height/2, z_center,
                                wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)

            # Правая стена (аналогично)
            # Строим только если ix == rooms_x-1 (внешняя) или если есть проём
            if ix == rooms_x - 1:
                create_wall(x_center + room_w/2 + wall_thick/2, height/2, z_center,
                            wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                # Проверяем проход между (ix, iz) и (ix+1, iz)
                if random.random() < door_prob:
                    door_z = z_center
                    left_width = room_d/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center + room_w/2 + wall_thick/2, height/2,
                                    z_center - left_width/2,
                                    wall_thick, height, left_width, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_d/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center + room_w/2 + wall_thick/2, height/2,
                                    z_center + right_width/2,
                                    wall_thick, height, right_width, color.dark_gray, TEXTURE_WALL_INNER)
                    create_door(x_center + room_w/2 + wall_thick/2 + 0.05, door_h/2, z_center,
                                door_w, door_h)
                else:
                    create_wall(x_center + room_w/2 + wall_thick/2, height/2, z_center,
                                wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)

            # Нижняя стена (по Z-)
            if iz == 0:
                create_wall(x_center, height/2, z_center - room_d/2 - wall_thick/2,
                            room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                # проход между (ix, iz-1) и (ix, iz)
                if random.random() < door_prob:
                    door_x = x_center
                    left_width = room_w/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center - left_width/2, height/2,
                                    z_center - room_d/2 - wall_thick/2,
                                    left_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_w/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center + right_width/2, height/2,
                                    z_center - room_d/2 - wall_thick/2,
                                    right_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                    create_door(x_center, door_h/2, z_center - room_d/2 - wall_thick/2 - 0.05,
                                door_w, door_h)
                else:
                    create_wall(x_center, height/2, z_center - room_d/2 - wall_thick/2,
                                room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)

            # Верхняя стена (по Z+)
            if iz == rooms_z - 1:
                create_wall(x_center, height/2, z_center + room_d/2 + wall_thick/2,
                            room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                if random.random() < door_prob:
                    door_x = x_center
                    left_width = room_w/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center - left_width/2, height/2,
                                    z_center + room_d/2 + wall_thick/2,
                                    left_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_w/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center + right_width/2, height/2,
                                    z_center + room_d/2 + wall_thick/2,
                                    right_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                    create_door(x_center, door_h/2, z_center + room_d/2 + wall_thick/2 + 0.05,
                                door_w, door_h)
                else:
                    create_wall(x_center, height/2, z_center + room_d/2 + wall_thick/2,
                                room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)

    # Добавляем освещение (несколько источников, чтобы осветить всю сетку)
    # Можно добавить по одному свету в каждую комнату
    for ix in range(rooms_x):
        for iz in range(rooms_z):
            x_center = -half_x + wall_thick + ix * (room_w + wall_thick) + room_w/2
            z_center = -half_z + wall_thick + iz * (room_d + wall_thick) + room_d/2
            PointLight(position=(x_center, height - 0.5, z_center),
                       color=color.white, intensity=2, range=30)

    return room_centers, []   # exit_doors не используем