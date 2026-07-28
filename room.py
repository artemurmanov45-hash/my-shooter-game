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

def generate_floor(floor_level, hole_center=None):
    """Генерирует один этаж на заданном уровне (0 или -1). Возвращает список центров комнат."""
    global building_objects
    rooms_x = GRID_ROOMS_X
    rooms_z = GRID_ROOMS_Z
    room_w = GRID_ROOM_WIDTH
    room_d = GRID_ROOM_DEPTH
    wall_thick = GRID_WALL_THICKNESS
    door_w = GRID_DOOR_WIDTH
    door_h = GRID_DOOR_HEIGHT
    door_prob = GRID_DOOR_PROBABILITY
    height = WALL_HEIGHT
    hole_size = HOLE_SIZE

    y_base = floor_level * height

    total_width = rooms_x * room_w + (rooms_x + 1) * wall_thick
    total_depth = rooms_z * room_d + (rooms_z + 1) * wall_thick
    half_x = total_width / 2
    half_z = total_depth / 2

    room_centers = []

    for ix in range(rooms_x):
        for iz in range(rooms_z):
            x_center = -half_x + wall_thick + ix * (room_w + wall_thick) + room_w/2
            z_center = -half_z + wall_thick + iz * (room_d + wall_thick) + room_d/2
            room_centers.append((x_center, z_center))

            is_hole = (hole_center and ix == hole_center[0] and iz == hole_center[1])

            # ----- СОЗДАНИЕ ПОЛА (с учётом отверстия) -----
            if is_hole:
                # Центральная комната – пол из 4 частей вокруг отверстия
                # Верхняя часть
                top_height = (room_d - hole_size) / 2
                if top_height > 0:
                    z_top = z_center + (room_d + hole_size) / 4
                    create_floor(x_center, y_base, z_top, room_w, top_height, color.gray, TEXTURE_FLOOR)
                # Нижняя часть
                bottom_height = (room_d - hole_size) / 2
                if bottom_height > 0:
                    z_bottom = z_center - (room_d + hole_size) / 4
                    create_floor(x_center, y_base, z_bottom, room_w, bottom_height, color.gray, TEXTURE_FLOOR)
                # Левая часть
                left_width = (room_w - hole_size) / 2
                if left_width > 0:
                    x_left = x_center - (room_w + hole_size) / 4
                    create_floor(x_left, y_base, z_center, left_width, hole_size, color.gray, TEXTURE_FLOOR)
                # Правая часть
                right_width = (room_w - hole_size) / 2
                if right_width > 0:
                    x_right = x_center + (room_w + hole_size) / 4
                    create_floor(x_right, y_base, z_center, right_width, hole_size, color.gray, TEXTURE_FLOOR)
                # Можно добавить визуальное обозначение отверстия (чёрный куб или красную рамку)
                # Пока оставим просто пустоту
            else:
                create_floor(x_center, y_base, z_center, room_w, room_d, color.gray, TEXTURE_FLOOR)

            # Потолок (всегда целый)
            create_ceiling(x_center, y_base + height, z_center, room_w, room_d, color.light_gray, TEXTURE_CEILING)

            # ----- СТЕНЫ (без изменений) -----
            # Левая
            if ix == 0:
                create_wall(x_center - room_w/2 - wall_thick/2, y_base + height/2, z_center,
                            wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                if random.random() < door_prob:
                    door_z = z_center
                    left_width = room_d/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center - room_w/2 - wall_thick/2, y_base + height/2,
                                    z_center - left_width/2,
                                    wall_thick, height, left_width, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_d/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center - room_w/2 - wall_thick/2, y_base + height/2,
                                    z_center + right_width/2,
                                    wall_thick, height, right_width, color.dark_gray, TEXTURE_WALL_INNER)
                else:
                    create_wall(x_center - room_w/2 - wall_thick/2, y_base + height/2, z_center,
                                wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)

            # Правая
            if ix == rooms_x - 1:
                create_wall(x_center + room_w/2 + wall_thick/2, y_base + height/2, z_center,
                            wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                if random.random() < door_prob:
                    door_z = z_center
                    left_width = room_d/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center + room_w/2 + wall_thick/2, y_base + height/2,
                                    z_center - left_width/2,
                                    wall_thick, height, left_width, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_d/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center + room_w/2 + wall_thick/2, y_base + height/2,
                                    z_center + right_width/2,
                                    wall_thick, height, right_width, color.dark_gray, TEXTURE_WALL_INNER)
                else:
                    create_wall(x_center + room_w/2 + wall_thick/2, y_base + height/2, z_center,
                                wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)

            # Нижняя
            if iz == 0:
                create_wall(x_center, y_base + height/2, z_center - room_d/2 - wall_thick/2,
                            room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                if random.random() < door_prob:
                    door_x = x_center
                    left_width = room_w/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center - left_width/2, y_base + height/2,
                                    z_center - room_d/2 - wall_thick/2,
                                    left_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_w/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center + right_width/2, y_base + height/2,
                                    z_center - room_d/2 - wall_thick/2,
                                    right_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                else:
                    create_wall(x_center, y_base + height/2, z_center - room_d/2 - wall_thick/2,
                                room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)

            # Верхняя
            if iz == rooms_z - 1:
                create_wall(x_center, y_base + height/2, z_center + room_d/2 + wall_thick/2,
                            room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                if random.random() < door_prob:
                    door_x = x_center
                    left_width = room_w/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center - left_width/2, y_base + height/2,
                                    z_center + room_d/2 + wall_thick/2,
                                    left_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_w/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center + right_width/2, y_base + height/2,
                                    z_center + room_d/2 + wall_thick/2,
                                    right_width, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
                else:
                    create_wall(x_center, y_base + height/2, z_center + room_d/2 + wall_thick/2,
                                room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)

    # Освещение
    for ix in range(rooms_x):
        for iz in range(rooms_z):
            x_center = -half_x + wall_thick + ix * (room_w + wall_thick) + room_w/2
            z_center = -half_z + wall_thick + iz * (room_d + wall_thick) + room_d/2
            PointLight(position=(x_center, y_base + height - 0.5, z_center),
                       color=color.white, intensity=2, range=30)

    return room_centers

def generate_grid_rooms():
    """Генерирует два этажа: первый (0) и подвал (-1) с отверстием в центре первого этажа."""
    global building_objects
    building_objects.clear()

    all_room_centers = []

    # Центральная комната (индексы)
    center_x = GRID_ROOMS_X // 2
    center_z = GRID_ROOMS_Z // 2

    # Первый этаж – с отверстием
    centers_floor0 = generate_floor(0, hole_center=(center_x, center_z))
    all_room_centers.extend(centers_floor0)

    # Подвал – без отверстия
    centers_floor1 = generate_floor(-1, hole_center=None)
    all_room_centers.extend(centers_floor1)

    return all_room_centers, []