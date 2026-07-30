
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

    return room_centers, []