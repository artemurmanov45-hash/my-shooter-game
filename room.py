# room.py
from ursina import *
from settings import *

def create_window(x, y, z, width=1.5, height=1.5):
    frame_color = color.rgb(100, 80, 60)
    glass_color = color.rgba(150, 200, 255, 100)
    Entity(model='cube', color=glass_color, scale=(width, height, 0.05), position=(x, y, z))
    Entity(model='cube', color=frame_color, scale=(width, 0.05, 0.1), position=(x, y + height/2, z))
    Entity(model='cube', color=frame_color, scale=(width, 0.05, 0.1), position=(x, y - height/2, z))
    Entity(model='cube', color=frame_color, scale=(0.05, height, 0.1), position=(x - width/2, y, z))
    Entity(model='cube', color=frame_color, scale=(0.05, height, 0.1), position=(x + width/2, y, z))
    Entity(model='cube', color=frame_color, scale=(width, 0.03, 0.1), position=(x, y, z))

def create_textured_entity(model, texture, default_color, **kwargs):
    """Пытается создать Entity с текстурой, при ошибке использует цвет и выводит предупреждение."""
    try:
        return Entity(model=model, texture=texture, **kwargs)
    except Exception as e:
        print(f"Не удалось загрузить текстуру '{texture}'. Использую цвет. Ошибка: {e}")
        return Entity(model=model, color=default_color, **kwargs)

def create_room(x_offset, z_offset,
                has_left_door=False, has_right_door=False,
                has_front_door=False, has_back_door=False,
                has_window_left=False, has_window_right=False,
                has_window_front=False, has_window_back=False):
    half = ROOM_SIZE / 2
    y_center = WALL_HEIGHT / 2

    # Пол
    floor = create_textured_entity('cube', TEXTURE_FLOOR, color.gray,
                                   scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
                                   position=(x_offset, -0.05, z_offset), collider='box')
    # Потолок
    ceiling = create_textured_entity('cube', TEXTURE_CEILING, color.light_gray,
                                     scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
                                     position=(x_offset, WALL_HEIGHT, z_offset))

    # Стены
    wall_z_neg = create_textured_entity('cube', TEXTURE_WALL, color.dark_gray,
                                        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
                                        position=(x_offset, y_center, z_offset - half), collider='box')
    wall_z_pos = create_textured_entity('cube', TEXTURE_WALL, color.dark_gray,
                                        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
                                        position=(x_offset, y_center, z_offset + half), collider='box')
    wall_x_neg = create_textured_entity('cube', TEXTURE_WALL, color.dark_gray,
                                        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
                                        position=(x_offset - half, y_center, z_offset), collider='box')
    wall_x_pos = create_textured_entity('cube', TEXTURE_WALL, color.dark_gray,
                                        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
                                        position=(x_offset + half, y_center, z_offset), collider='box')

    # Двери (без текстур, цветные)
    door_color = color.rgb(100, 80, 60)
    if has_left_door:
        destroy(wall_x_neg)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(model='cube', color=door_color, scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset - half, y_center, z_offset - half_door/2), collider='box')
        Entity(model='cube', color=door_color, scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset - half, y_center, z_offset + half_door/2), collider='box')
        Entity(model='cube', color=door_color, scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
               position=(x_offset - half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset), collider='box')
    if has_right_door:
        destroy(wall_x_pos)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(model='cube', color=door_color, scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset + half, y_center, z_offset - half_door/2), collider='box')
        Entity(model='cube', color=door_color, scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset + half, y_center, z_offset + half_door/2), collider='box')
        Entity(model='cube', color=door_color, scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
               position=(x_offset + half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset), collider='box')
    if has_front_door:
        destroy(wall_z_pos)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(model='cube', color=door_color, scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
               position=(x_offset - half_door/2, y_center, z_offset + half), collider='box')
        Entity(model='cube', color=door_color, scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
               position=(x_offset + half_door/2, y_center, z_offset + half), collider='box')
        Entity(model='cube', color=door_color, scale=(DOOR_WIDTH, WALL_HEIGHT - DOOR_HEIGHT, WALL_THICKNESS),
               position=(x_offset, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset + half), collider='box')
    if has_back_door:
        destroy(wall_z_neg)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(model='cube', color=door_color, scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
               position=(x_offset - half_door/2, y_center, z_offset - half), collider='box')
        Entity(model='cube', color=door_color, scale=(half_door, WALL_HEIGHT, WALL_THICKNESS),
               position=(x_offset + half_door/2, y_center, z_offset - half), collider='box')
        Entity(model='cube', color=door_color, scale=(DOOR_WIDTH, WALL_HEIGHT - DOOR_HEIGHT, WALL_THICKNESS),
               position=(x_offset, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset - half), collider='box')

    # Окна
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

    # Свет
    PointLight(position=(x_offset, WALL_HEIGHT - 0.3, z_offset),
               color=color.rgb(255, 240, 200), intensity=2.0, range=30)
    Entity(model='cube', color=color.rgb(200, 200, 200),
           scale=(0.3, 0.1, 0.3), position=(x_offset, WALL_HEIGHT - 0.1, z_offset))

def generate_rooms():
    offset_x = -(GRID_SIZE - 1) * ROOM_SIZE / 2
    offset_z = -(GRID_SIZE - 1) * ROOM_SIZE / 2
    room_centers = []
    for ix in range(GRID_SIZE):
        for iz in range(GRID_SIZE):
            x = ix * ROOM_SIZE + offset_x
            z = iz * ROOM_SIZE + offset_z
            room_centers.append((x, z))
            has_left = (ix > 0)
            has_right = (ix < GRID_SIZE - 1)
            has_front = (iz < GRID_SIZE - 1)
            has_back = (iz > 0)
            win_left = (ix == 0)
            win_right = (ix == GRID_SIZE - 1)
            win_front = (iz == GRID_SIZE - 1)
            win_back = (iz == 0)
            create_room(x, z,
                        has_left_door=has_left,
                        has_right_door=has_right,
                        has_front_door=has_front,
                        has_back_door=has_back,
                        has_window_left=win_left,
                        has_window_right=win_right,
                        has_window_front=win_front,
                        has_window_back=win_back)
    # Дверные рамы
    for ix in range(GRID_SIZE):
        for iz in range(GRID_SIZE):
            x = ix * ROOM_SIZE + offset_x
            z = iz * ROOM_SIZE + offset_z
            if ix < GRID_SIZE - 1:
                Entity(model='cube', color=color.rgb(100, 80, 60),
                       scale=(0.1, DOOR_HEIGHT, DOOR_WIDTH + 0.2),
                       position=(x + ROOM_SIZE/2, DOOR_HEIGHT/2, z))
            if iz < GRID_SIZE - 1:
                Entity(model='cube', color=color.rgb(100, 80, 60),
                       scale=(DOOR_WIDTH + 0.2, DOOR_HEIGHT, 0.1),
                       position=(x, DOOR_HEIGHT/2, z + ROOM_SIZE/2))
    return room_centers