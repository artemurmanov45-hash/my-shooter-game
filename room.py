from ursina import *
from settings import *
import random
import os

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
    thickness = 1.0
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

def place_picture(position, normal, height_center, texture_path=None, size=None):
    """
    Размещает одну картину в заданной позиции.
    """
    if size is None:
        size = PICTURE_SIZE if 'PICTURE_SIZE' in globals() else 1.5

    pic_pos = Vec3(position.x, height_center, position.z)
    print(f"[place_picture] Размещаем картину на позиции {pic_pos}, нормаль {normal}")

    if texture_path is None:
        folder = PAINTING_FOLDER if 'PAINTING_FOLDER' in globals() else 'textures/paintings/'
        if os.path.exists(folder):
            valid_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.tga')
            files = [f for f in os.listdir(folder) if f.lower().endswith(valid_ext)]
            if files:
                texture_path = os.path.join(folder, random.choice(files))
                print(f"[place_picture] Выбрана текстура: {texture_path}")

    if texture_path and os.path.exists(texture_path):
        texture = texture_path
        clr = color.white
        print(f"[place_picture] Используем текстуру {texture_path}")
    else:
        texture = None
        clr = color.magenta
        print("[place_picture] Текстура не найдена, используем малиновый цвет")

    picture = Entity(
        model='quad',
        scale=(size, size),
        position=pic_pos,
        texture=texture,
        color=clr,
        double_sided=True,
        collider=None,
        parent=scene
    )
    picture.look_at(pic_pos + normal)
    building_objects.append(picture)
    return picture

def generate_grid_rooms():
    global building_objects
    building_objects.clear()

    rooms_x = GRID_ROOMS_X
    rooms_z = GRID_ROOMS_Z
    room_w = GRID_ROOM_WIDTH
    room_d = GRID_ROOM_DEPTH
    wall_thick = GRID_WALL_THICKNESS
    door_w = GRID_DOOR_WIDTH
    door_h = GRID_DOOR_HEIGHT
    door_prob = GRID_DOOR_PROBABILITY
    height = WALL_HEIGHT
    picture_h = PICTURE_HEIGHT if 'PICTURE_HEIGHT' in globals() else 1.7
    painting_count = PAINTING_COUNT if 'PAINTING_COUNT' in globals() else 2
    spacing = PICTURE_SPACING if 'PICTURE_SPACING' in globals() else 2.0

    total_width = rooms_x * room_w + (rooms_x + 1) * wall_thick
    total_depth = rooms_z * room_d + (rooms_z + 1) * wall_thick
    half_x = total_width / 2
    half_z = total_depth / 2

    create_floor(0, 0, 0, total_width, total_depth, color.gray, TEXTURE_FLOOR)
    create_ceiling(0, height, 0, total_width, total_depth, color.light_gray, TEXTURE_CEILING)

    room_centers = []

    for ix in range(rooms_x):
        for iz in range(rooms_z):
            x_center = -half_x + wall_thick + ix * (room_w + wall_thick) + room_w/2
            z_center = -half_z + wall_thick + iz * (room_d + wall_thick) + room_d/2
            room_centers.append((x_center, z_center))

            # Левая стена
            if ix == 0:
                create_wall(x_center - room_w/2 - wall_thick/2, height/2, z_center,
                            wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)
            else:
                if random.random() < door_prob:
                    door_z = z_center
                    left_width = room_d/2 - door_w/2
                    if left_width > 0:
                        create_wall(x_center - room_w/2 - wall_thick/2, height/2,
                                    z_center - left_width/2,
                                    wall_thick, height, left_width, color.dark_gray, TEXTURE_WALL_INNER)
                    right_width = room_d/2 - door_w/2
                    if right_width > 0:
                        create_wall(x_center - room_w/2 - wall_thick/2, height/2,
                                    z_center + right_width/2,
                                    wall_thick, height, right_width, color.dark_gray, TEXTURE_WALL_INNER)
                else:
                    create_wall(x_center - room_w/2 - wall_thick/2, height/2, z_center,
                                wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)

            # Правая стена
            if ix == rooms_x - 1:
                create_wall(x_center + room_w/2 + wall_thick/2, height/2, z_center,
                            wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)
            else:
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
                else:
                    create_wall(x_center + room_w/2 + wall_thick/2, height/2, z_center,
                                wall_thick, height, room_d, color.dark_gray, TEXTURE_WALL_INNER)

            # Нижняя стена
            if iz == 0:
                create_wall(x_center, height/2, z_center - room_d/2 - wall_thick/2,
                            room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)
            else:
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
                else:
                    create_wall(x_center, height/2, z_center - room_d/2 - wall_thick/2,
                                room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)

            # Верхняя стена
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
                else:
                    create_wall(x_center, height/2, z_center + room_d/2 + wall_thick/2,
                                room_w, height, wall_thick, color.dark_gray, TEXTURE_WALL_INNER)

    # ---- РАЗМЕЩАЕМ КАРТИНЫ ВРУЧНУЮ НА ПРАВОЙ СТЕНЕ ПЕРВОЙ КОМНАТЫ ----
    first_room_x = -half_x + wall_thick + room_w/2
    first_room_z = -half_z + wall_thick + room_d/2

    # Правая стена: её центр по X = first_room_x + room_w/2 + wall_thick/2
    wall_x = first_room_x + room_w/2 + wall_thick/2
    # Внутренняя поверхность: вычитаем половину толщины, чтобы картина была внутри комнаты
    pic_x = wall_x - wall_thick/2 - 0.01  # чуть внутрь

    print(f"[DEBUG] Первая комната центр: ({first_room_x}, {first_room_z})")
    print(f"[DEBUG] Правая стена центр X: {wall_x}, картина X: {pic_x}")

    # Подготавливаем текстуры
    folder = PAINTING_FOLDER if 'PAINTING_FOLDER' in globals() else 'textures/paintings/'
    textures = []
    if os.path.exists(folder):
        valid_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.tga')
        files = [f for f in os.listdir(folder) if f.lower().endswith(valid_ext)]
        textures = [os.path.join(folder, f) for f in files]
        print(f"[DEBUG] Найдено текстур: {len(textures)}")
    else:
        print(f"[DEBUG] Папка {folder} не найдена")

    if len(textures) < painting_count:
        textures += [None] * (painting_count - len(textures))

    offset = spacing / 2
    for i in range(painting_count):
        z_offset = -offset + i * spacing
        pic_z = first_room_z + z_offset
        pic_pos = Vec3(pic_x, picture_h, pic_z)
        tex = textures[i] if i < len(textures) else None
        print(f"[DEBUG] Размещаем картину {i+1} на позиции {pic_pos}, текстура {tex}")
        place_picture(pic_pos, Vec3(-1, 0, 0), picture_h, tex)

    print(f"[Картины] Размещено {painting_count} картин на правой стене первой комнаты.")
    return room_centers, []