from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
from math import sin
import sys

app = Ursina(borderless=False)

# ------------------ ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ------------------
player = None
enemies = []
score = 0
score_text = None
gun = None
game_started = False
menu_entities = []

# ------------------ НАСТРОЙКИ ------------------
ROOM_SIZE = 40
WALL_HEIGHT = 6.0
WALL_THICKNESS = 0.2
DOOR_WIDTH = 2.0
DOOR_HEIGHT = 3.0
WINDOW_WIDTH = 1.5
WINDOW_HEIGHT = 1.5
WINDOW_Y = 1.8

# ------------------ ФУНКЦИИ МЕНЮ ------------------
def create_menu():
    bg = Entity(model='quad', scale=(50,30), color=color.rgba(0,0,0,200), z=1)
    menu_entities.append(bg)
    title_shadow = Text(text='CUPER', scale=5, origin=(0,0), position=(0.02,0.32),
                        color=color.rgba(0,0,0,100), font='VeraMono.ttf')
    menu_entities.append(title_shadow)
    title = Text(text='CUPER', scale=5, origin=(0,0), position=(0,0.3),
                 color=color.gold, font='VeraMono.ttf')
    menu_entities.append(title)
    start_btn = Button(text='Начать новую игру', scale=(0.3,0.07), position=(0,0.05),
                       color=color.azure, text_color=color.white, font='VeraMono.ttf')
    start_btn.on_click = start_game
    menu_entities.append(start_btn)
    exit_btn = Button(text='Выход', scale=(0.2,0.05), position=(0,-0.1),
                      color=color.red, text_color=color.white, font='VeraMono.ttf')
    exit_btn.on_click = sys.exit
    menu_entities.append(exit_btn)

def destroy_menu():
    global menu_entities
    for e in menu_entities:
        destroy(e)
    menu_entities.clear()

# ------------------ КЛАСС ГУМАНОИДНОГО ВРАГА ------------------
class HumanoidEnemy(Entity):
    def __init__(self, position=(0,0,0), color=color.red):
        super().__init__(position=position)
        self.height = 1.8
        self.speed = 1.5
        self.alive = True
        self.walk_time = 0
        self.walk_amplitude = 0.3

        # Торс (используем RGBA кортежи)
        self.torso = Entity(
            parent=self,
            model='cube',
            color=(50, 50, 80, 255),
            scale=(0.6, 0.6, 0.3),
            position=(0, self.height*0.6, 0),
            collider='box'
        )
        self.head = Entity(
            parent=self,
            model='sphere',
            color=(255, 200, 150, 255),
            scale=0.3,
            position=(0, self.height*0.9, 0)
        )
        self.arm_left = Entity(
            parent=self,
            model='cube',
            color=(80, 80, 120, 255),
            scale=(0.12, 0.5, 0.12),
            position=(-0.4, self.height*0.7, 0),
            rotation=(0, 0, 10)
        )
        self.arm_right = Entity(
            parent=self,
            model='cube',
            color=(80, 80, 120, 255),
            scale=(0.12, 0.5, 0.12),
            position=(0.4, self.height*0.7, 0),
            rotation=(0, 0, -10)
        )
        self.leg_left = Entity(
            parent=self,
            model='cube',
            color=(40, 40, 60, 255),
            scale=(0.15, 0.5, 0.15),
            position=(-0.15, self.height*0.2, 0)
        )
        self.leg_right = Entity(
            parent=self,
            model='cube',
            color=(40, 40, 60, 255),
            scale=(0.15, 0.5, 0.15),
            position=(0.15, self.height*0.2, 0)
        )

    def update(self):
        if not self.alive or not player:
            return
        dir_to_player = player.position - self.position
        dir_to_player.y = 0
        distance = dir_to_player.length()

        if distance > 0.5:
            self.look_at(Vec3(player.position.x, self.y, player.position.z))
            move_vec = dir_to_player.normalized() * time.dt * self.speed
            self.position += move_vec
            self.walk_time += time.dt * 10
            self.leg_left.rotation_x = self.walk_amplitude * sin(self.walk_time)
            self.leg_right.rotation_x = self.walk_amplitude * sin(self.walk_time + 3.14)
            self.arm_left.rotation_x = -self.walk_amplitude * 0.5 * sin(self.walk_time)
            self.arm_right.rotation_x = -self.walk_amplitude * 0.5 * sin(self.walk_time + 3.14)
        else:
            self.leg_left.rotation_x = 0
            self.leg_right.rotation_x = 0
            self.arm_left.rotation_x = 0
            self.arm_right.rotation_x = 0

        if distance < 1.5 and self.alive:
            self.alive = False
            self.disable()

    def die(self):
        self.alive = False
        self.disable()

def create_humanoid_enemy():
    room = random.choice(['left', 'center', 'right'])
    if room == 'left':
        x = random.uniform(-35, -5)
    elif room == 'center':
        x = random.uniform(-18, 18)
    else:
        x = random.uniform(5, 35)
    z = random.uniform(-18, 18)
    colors = [color.red, color.orange, color.yellow, color.green, color.cyan, color.magenta]
    enemy_color = random.choice(colors)
    return HumanoidEnemy(position=(x, 0, z), color=enemy_color)

# ------------------ ФУНКЦИИ ПОСТРОЕНИЯ ------------------
def create_window(x, y, z, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
    frame_color = (100, 80, 60, 255)
    glass = Entity(
        model='cube',
        color=(150, 200, 255, 100),  # полупрозрачное стекло
        scale=(width, height, 0.05),
        position=(x, y, z)
    )
    Entity(model='cube', color=frame_color, scale=(width, 0.05, 0.1), position=(x, y + height/2, z))
    Entity(model='cube', color=frame_color, scale=(width, 0.05, 0.1), position=(x, y - height/2, z))
    Entity(model='cube', color=frame_color, scale=(0.05, height, 0.1), position=(x - width/2, y, z))
    Entity(model='cube', color=frame_color, scale=(0.05, height, 0.1), position=(x + width/2, y, z))
    Entity(model='cube', color=frame_color, scale=(width, 0.03, 0.1), position=(x, y, z))

def create_room(x_offset, z_offset,
                has_left_door=False, has_right_door=False,
                has_window_left=False, has_window_right=False,
                has_window_front=False, has_window_back=False,
                floor_texture='wood', wall_texture='brick'):
    half = ROOM_SIZE / 2
    y_center = WALL_HEIGHT / 2

    # Пол
    floor = Entity(
        model='cube',
        texture=floor_texture,
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, -0.05, z_offset),
        collider='box',
        color=(60, 40, 30, 255)  # тёмный оттенок
    )
    # Потолок (светлая плитка) – можно оставить цвет
    ceiling = Entity(
        model='cube',
        texture='stone',        # встроенная текстура
        scale=(ROOM_SIZE, 0.1, ROOM_SIZE),
        position=(x_offset, WALL_HEIGHT, z_offset),
        color=(230, 230, 230, 255)
    )

    # Стены с текстурой кирпича
    wall_color = None  # используем текстуру, цвет не задаём
    wall_z_neg = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset - half),
        collider='box'
    )
    wall_z_pos = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),
        scale=(ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS),
        position=(x_offset, y_center, z_offset + half),
        collider='box'
    )
    wall_x_neg = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset - half, y_center, z_offset),
        collider='box'
    )
    wall_x_pos = Entity(
        model='cube',
        texture=wall_texture,
        texture_scale=(8, 8),
        scale=(WALL_THICKNESS, WALL_HEIGHT, ROOM_SIZE),
        position=(x_offset + half, y_center, z_offset),
        collider='box'
    )

    # Двери
    if has_left_door:
        destroy(wall_x_neg)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(model='cube', texture=wall_texture, texture_scale=(8,8),
               scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset - half, y_center, z_offset - half_door/2), collider='box')
        Entity(model='cube', texture=wall_texture, texture_scale=(8,8),
               scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset - half, y_center, z_offset + half_door/2), collider='box')
        Entity(model='cube', texture=wall_texture, texture_scale=(8,8),
               scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
               position=(x_offset - half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset), collider='box')
    if has_right_door:
        destroy(wall_x_pos)
        half_door = (ROOM_SIZE - DOOR_WIDTH) / 2
        Entity(model='cube', texture=wall_texture, texture_scale=(8,8),
               scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset + half, y_center, z_offset - half_door/2), collider='box')
        Entity(model='cube', texture=wall_texture, texture_scale=(8,8),
               scale=(WALL_THICKNESS, WALL_HEIGHT, half_door),
               position=(x_offset + half, y_center, z_offset + half_door/2), collider='box')
        Entity(model='cube', texture=wall_texture, texture_scale=(8,8),
               scale=(WALL_THICKNESS, WALL_HEIGHT - DOOR_HEIGHT, DOOR_WIDTH),
               position=(x_offset + half, (WALL_HEIGHT - DOOR_HEIGHT)/2 + DOOR_HEIGHT, z_offset), collider='box')

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

    # Освещение
    PointLight(
        position=(x_offset, WALL_HEIGHT - 0.3, z_offset),
        color=(255, 240, 200, 255),
        intensity=2.0,
        range=30
    )
    Entity(
        model='cube',
        color=(200, 200, 200, 255),
        scale=(0.3, 0.1, 0.3),
        position=(x_offset, WALL_HEIGHT - 0.1, z_offset)
    )

# ------------------ ЗАПУСК ИГРЫ (обёртка) ------------------
def start_game():
    global player, enemies, score, score_text, gun, game_started
    destroy_menu()

    # ---- ПОСТРОЕНИЕ ТРЁХ КОМНАТ ----
    create_room(-40, 0, has_right_door=True,
                has_window_left=True, has_window_front=True, has_window_back=True)
    create_room(0, 0, has_left_door=True, has_right_door=True,
                has_window_front=True, has_window_back=True)
    create_room(40, 0, has_left_door=True,
                has_window_right=True, has_window_front=True, has_window_back=True)

    # Дверные рамы
    frame1 = Entity(model='cube', color=(100, 80, 60, 255),
                    scale=(0.1, DOOR_HEIGHT, DOOR_WIDTH + 0.2), position=(-20, DOOR_HEIGHT/2, 0))
    frame2 = Entity(model='cube', color=(100, 80, 60, 255),
                    scale=(0.1, DOOR_HEIGHT, DOOR_WIDTH + 0.2), position=(20, DOOR_HEIGHT/2, 0))

    # ---- ИГРОК ----
    player = FirstPersonController()
    player.position = (-30, 1, 0)

    # ---- ОРУЖИЕ ----
    gun = Entity(parent=camera, model='cube', color=(60, 60, 60, 255),
                 scale=(0.2, 0.1, 0.5), position=(0.3, -0.2, 0.5))
    barrel = Entity(parent=gun, model='cube', color=(0, 0, 0, 255),
                    scale=(0.1, 0.08, 0.2), position=(0, 0, 0.35))
    grip = Entity(parent=gun, model='cube', color=(139, 69, 19, 255),
                  scale=(0.12, 0.2, 0.1), position=(0, -0.15, -0.1))

    # ---- ВРАГИ (20 штук) ----
    enemies = []
    for _ in range(20):
        enemies.append(create_humanoid_enemy())

    score = 0
    score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2)
    game_started = True
    mouse.locked = True
    mouse.visible = False

def update():
    global score
    if not game_started:
        return
    for enemy in enemies[:]:
        if not enemy.alive:
            enemies.remove(enemy)
            enemies.append(create_humanoid_enemy())
            score += 1
    if score_text:
        score_text.text = f'Score: {score}'

def input(key):
    global score
    if not game_started:
        return
    if key == 'left mouse down':
        gun.position = (0.3, -0.2, 0.3)
        invoke(setattr, gun, 'position', (0.3, -0.2, 0.5), delay=0.1)

        hit_info = raycast(player.position + player.forward*0.5, player.forward, distance=50)
        if hit_info.hit:
            for enemy in enemies:
                if enemy == hit_info.entity or hit_info.entity in enemy.children:
                    enemy.die()
                    break
    if key == 'escape':
        sys.exit()

# ------------------ СТАРТ ------------------
mouse.locked = False
mouse.visible = True
create_menu()
AmbientLight(color=(50, 50, 50, 0.3))
app.run()