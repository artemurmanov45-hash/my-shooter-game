from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time
import sys
import os

import settings
from settings import GRID_SIZE, ROOM_SIZE, DOOR_WIDTH, WALL_HEIGHT
from room import generate_grid_rooms, building_objects
from player import create_player
from ui import create_ui, create_ammo_ui, update_ammo_ui
from enemy import Enemy, spawn_enemy, spawn_explosion

# ------------------ ДИАГНОСТИКА ------------------
print("=== НАЧАЛО СКРИПТА ===")
print("Текущая директория:", os.getcwd())
print("Интерпретатор Python:", sys.executable)
print("Аргументы командной строки:", sys.argv)
print("Версия Python:", sys.version)
print("==========================================")

app = Ursina(borderless=False, size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
application.fps = 60
window.vsync = False

# ------------------ ЗВУКИ И МУЗЫКА ------------------
try:
    gunshot_sound = Audio(settings.SOUND_GUNSHOT, loop=False, autoplay=False,
                          volume=getattr(settings, 'VOLUME_GUNSHOT', 1.0))
    enemy_shot_sound = Audio(settings.SOUND_ENEMY_SHOT, loop=False, autoplay=False,
                             volume=getattr(settings, 'VOLUME_ENEMY_SHOT', 1.0))
    hit_sound = Audio(settings.SOUND_HIT, loop=False, autoplay=False,
                      volume=getattr(settings, 'VOLUME_HIT', 1.0))
    menu_click_sound = Audio(settings.SOUND_MENU_CLICK, loop=False, autoplay=False,
                             volume=getattr(settings, 'VOLUME_MENU_CLICK', 1.0))
    menu_music = Audio(settings.SOUND_MENU_MUSIC, loop=True, autoplay=False,
                       volume=getattr(settings, 'VOLUME_MENU_MUSIC', 1.0))
    game_music = Audio(settings.SOUND_GAME_MUSIC, loop=True, autoplay=False,
                       volume=getattr(settings, 'VOLUME_GAME_MUSIC', 1.0))
    reload_sound = Audio(settings.SOUND_RELOAD, loop=False, autoplay=False,
                         volume=getattr(settings, 'VOLUME_RELOAD', 1.0))
except:
    gunshot_sound = None
    enemy_shot_sound = None
    hit_sound = None
    menu_click_sound = None
    menu_music = None
    game_music = None
    reload_sound = None
    print("Звуки не найдены, будут без звука.")

if menu_music:
    menu_music.play()

def play_click_and_pause_music():
    if menu_click_sound:
        menu_click_sound.volume = 1.0
        menu_click_sound.play()
    if menu_music and menu_music.playing:
        menu_music.stop()
        invoke(lambda: menu_music.play() if menu_music else None, delay=0.2)

# ------------------ ГЛАВНОЕ МЕНЮ ------------------
try:
    menu_bg_texture = settings.TEXTURE_MENU_BG
except:
    menu_bg_texture = None

if menu_bg_texture:
    menu_bg = Entity(model='quad', texture=menu_bg_texture, scale=(2, 2), z=1, parent=camera.ui)
else:
    menu_bg = Entity(model='quad', scale=(2, 2), color=color.black, z=1, parent=camera.ui)

logo = Text(text='CUPER v CUBE', position=(0, 0.35), origin=(0,0), scale=3, color=color.black,
            outline=2, outline_color=color.white, background=True,
            background_color=color.rgba(255, 255, 255, 80))

def on_start_click():
    play_click_and_pause_music()
    invoke(start_game, delay=0.1)

def on_exit_click():
    play_click_and_pause_music()
    invoke(application.quit, delay=0.2)

btn_start = Button(text='Новая игра', scale=(0.3, 0.1), position=(0, -0.1), color=color.azure, on_click=on_start_click)
btn_exit = Button(text='Выход', scale=(0.3, 0.1), position=(0, -0.25), color=color.red, on_click=on_exit_click)

game_started = False

player = None
weapons = []
active_weapon_index = 0
base_speed = 10
player_health = settings.PLAYER_MAX_HEALTH
health_text = None
message_text = None
ammo_text = None
enemies = []
game_over = False
bullets = []
enemy_bullets = []
last_damage_time = 0
damage_cooldown = 1.0
room_centers = []
exit_doors = []
health_packs = []
pickups = []
inventory = [None, None, None]
inventory_ui = []

# ---------- ПЕРЕМЕННЫЕ ДЛЯ ПАТРОНОВ ----------
ammo_clip = 100
ammo_reserve = 10000
max_clip = 100
reloading = False
reload_timer = 0
reload_time = 2.0

# ---------- ПЕРЕМЕННЫЕ ДЛЯ ВОЛН ----------
current_wave = 0
waves = [
    {'count': 10, 'health': 1,   'scale': 1,   'color': color.red,     'label': 'Волна 1: Обычные враги'},
    {'count': 5,  'health': 10,  'scale': 2,   'color': color.magenta, 'label': 'Волна 2: Боссы'},
    {'count': 3,  'health': 25,  'scale': 4,   'color': color.gold,    'label': 'Волна 3: Мегабоссы'},
]
wave_message_timer = 0

# ---------- ПРИЦЕЛИВАНИЕ ----------
aiming = False
default_fov = 90
aim_fov = 60
default_gun_pos = Vec3(0.3, -0.2, 0.5)
aim_gun_pos = Vec3(0.0, -0.05, 0.25)
reload_gun_pos = Vec3(0.2, -0.5, 0.2)
current_gun_pos = default_gun_pos
current_fov = default_fov
aim_speed = 8.0

# ---------- ОТДАЧА ----------
recoil_offset = Vec3(0, 0, 0)
recoil_target = Vec3(0, 0, 0)
recoil_speed = 12.0

fire_timer = 0
fire_interval = 1 / settings.FIRE_RATE

# ---------- КЛАСС ЛИФТА ----------
class Elevator:
    def __init__(self, position, floors=[0, -1]):
        self.position = position
        self.floors = floors
        self.current_floor = 0
        self.target_floor = 0
        self.moving = False
        self.speed = getattr(settings, 'ELEVATOR_SPEED', 4.0)
        self.y = 0.0
        self.target_y = 0.0
        self.door_progress = 1.0
        self.door_target = 1.0
        self.door_speed = 2.0

        cabin_width = 4.0
        cabin_depth = 4.0
        cabin_height = 5.0
        half_w = cabin_width / 2
        half_d = cabin_depth / 2

        shaft_height = WALL_HEIGHT * 2 + 0.5
        shaft_color = color.rgb(70, 70, 70)
        self.shaft_left = Entity(model='cube', color=shaft_color, scale=(0.2, shaft_height, cabin_depth + 1),
                                 position=(position[0] - half_w - 0.5, 0, position[1]))
        self.shaft_right = Entity(model='cube', color=shaft_color, scale=(0.2, shaft_height, cabin_depth + 1),
                                  position=(position[0] + half_w + 0.5, 0, position[1]))
        self.shaft_back = Entity(model='cube', color=shaft_color, scale=(cabin_width + 1, shaft_height, 0.2),
                                 position=(position[0], 0, position[1] - half_d - 0.5))
        for floor in self.floors:
            y_floor = floor * WALL_HEIGHT
            if WALL_HEIGHT - 3.0 > 0:
                Entity(model='cube', color=shaft_color, scale=(cabin_width + 1, WALL_HEIGHT - 3.0, 0.2),
                       position=(position[0], y_floor + 3.0 + (WALL_HEIGHT - 3.0)/2, position[1] + half_d + 0.5))
            Entity(model='cube', color=shaft_color, scale=(cabin_width + 1, 0.2, 0.2),
                   position=(position[0], y_floor + 0.1, position[1] + half_d + 0.5))
            side_width = (cabin_width + 1 - 3.0) / 2
            if side_width > 0:
                Entity(model='cube', color=shaft_color, scale=(side_width, 3.0, 0.2),
                       position=(position[0] - (cabin_width + 1)/2 + side_width/2, y_floor + 1.5, position[1] + half_d + 0.5))
                Entity(model='cube', color=shaft_color, scale=(side_width, 3.0, 0.2),
                       position=(position[0] + (cabin_width + 1)/2 - side_width/2, y_floor + 1.5, position[1] + half_d + 0.5))

        self.cabin = Entity(model='cube', color=color.rgb(80, 80, 80), scale=(cabin_width, cabin_height, cabin_depth),
                            position=(position[0], self.y + cabin_height/2, position[1]), collider='box')
        self.door_left = Entity(parent=self.cabin, model='cube', color=color.rgb(160, 160, 160),
                                scale=(cabin_width/2 - 0.1, cabin_height - 0.2, 0.1),
                                position=(-cabin_width/2 + 0.1, 0, cabin_depth/2 + 0.05))
        self.door_right = Entity(parent=self.cabin, model='cube', color=color.rgb(160, 160, 160),
                                 scale=(cabin_width/2 - 0.1, cabin_height - 0.2, 0.1),
                                 position=(cabin_width/2 - 0.1, 0, cabin_depth/2 + 0.05))

        self.call_buttons = []
        for i, floor in enumerate(self.floors):
            y_pos = floor * WALL_HEIGHT + 0.5
            btn = Entity(model='cube', color=color.green if i == 0 else color.gray, scale=(0.5, 0.5, 0.1),
                         position=(position[0] + half_w + 1.0, y_pos, position[1] + half_d + 0.5), collider='box')
            btn.floor_index = i
            Text(text=f'Вызов {i+1}', position=btn.position + Vec3(0, 0.4, 0), scale=0.3, color=color.white)
            self.call_buttons.append(btn)

    def call(self, floor_index):
        if self.moving:
            return
        if floor_index == self.current_floor:
            return
        self.door_target = 0.0
        self.target_floor = floor_index
        self.target_y = self.floors[floor_index] * WALL_HEIGHT
        self.moving = True
        for i, btn in enumerate(self.call_buttons):
            btn.color = color.red if i == floor_index else color.gray

    def toggle_doors(self):
        if not self.moving:
            self.door_target = 1.0 if self.door_progress < 0.5 else 0.0

    def update(self):
        if abs(self.door_progress - self.door_target) > 0.001:
            step = self.door_speed * time.dt
            if self.door_progress < self.door_target:
                self.door_progress = min(self.door_progress + step, self.door_target)
            else:
                self.door_progress = max(self.door_progress - step, self.door_target)
            cabin_width = self.cabin.scale_x
            offset = (cabin_width/2 - 0.1) * (1 - self.door_progress)
            self.door_left.x = -cabin_width/2 + 0.1 + offset
            self.door_right.x = cabin_width/2 - 0.1 - offset

        if self.moving:
            diff = self.target_y - self.y
            if abs(diff) > 0.01:
                step = self.speed * time.dt
                if abs(diff) < step:
                    self.y = self.target_y
                else:
                    self.y += step if diff > 0 else -step
                self.cabin.y = self.y + self.cabin.scale_y / 2
            else:
                self.y = self.target_y
                self.cabin.y = self.y + self.cabin.scale_y / 2
                self.moving = False
                self.current_floor = self.target_floor
                self.door_target = 1.0
                for i, btn in enumerate(self.call_buttons):
                    btn.color = color.green if i == self.current_floor else color.gray

    def get_floor_y(self, floor_index):
        return self.floors[floor_index] * WALL_HEIGHT

elevator = None
elevator_nearby = False
elevator_hint_text = None

# ---------- ФУНКЦИЯ СОЗДАНИЯ ПИКАПОВ (ИСПРАВЛЕНА) ----------
def spawn_weapon_pickups(count_per_floor):
    global pickups
    pickups.clear()
    model_path = getattr(settings, 'SECONDARY_WEAPON_MODEL', 'models/rifle.glb')
    scale = getattr(settings, 'SECONDARY_WEAPON_SCALE', 0.5)
    for floor in [0, -1]:
        y_base = floor * WALL_HEIGHT
        available = list(room_centers)
        random.shuffle(available)
        for i in range(min(count_per_floor, len(available))):
            cx, cz = available[i]
            x = cx + random.uniform(-10, 10)
            z = cz + random.uniform(-10, 10)
            y = y_base + 0.5
            # Всегда указываем цвет, чтобы избежать None
            pickup = Entity(
                model=model_path if os.path.exists(model_path) else 'cube',
                color=color.yellow if not os.path.exists(model_path) else color.white,
                position=(x, y, z),
                scale=scale,
                collider='box'
            )
            pickup.pickup_type = 'weapon'
            pickup.weapon_index = 1   # индекс второго оружия
            pickups.append(pickup)

# ---------- ФУНКЦИЯ ОБНОВЛЕНИЯ UI ИНВЕНТАРЯ ----------
def update_inventory_ui():
    global inventory_ui
    for item in inventory_ui:
        destroy(item)
    inventory_ui.clear()
    for i in range(3):
        color_ = color.gray if inventory[i] is None else color.white
        cell = Entity(model='quad', color=color_, scale=(0.05, 0.05), position=(-0.2 + i*0.1, -0.4), parent=camera.ui)
        if inventory[i] is not None:
            Text(text=str(i+1), position=(-0.2 + i*0.1, -0.43), scale=1, color=color.white, parent=camera.ui)
        inventory_ui.append(cell)

# ---------- ФУНКЦИЯ ПЕРЕКЛЮЧЕНИЯ ОРУЖИЯ ----------
def switch_weapon(index):
    global active_weapon_index
    if index < 0 or index >= len(weapons):
        return
    if inventory[index] is None:
        return
    weapons[active_weapon_index].entity.visible = False
    active_weapon_index = index
    weapons[active_weapon_index].entity.visible = True

# ---------- ФУНКЦИИ ДЛЯ ПУЛЬ, ПЕРЕЗАРЯДКИ И Т.Д. ----------
def create_enemy_bullet(start_pos, direction, damage=1):
    bullet = Entity(model='sphere', color=color.blue, scale=0.1,
                    position=start_pos, collider='sphere')
    bullet.direction = direction
    bullet.speed = 15
    bullet.lifetime = 3.0
    bullet.damage = damage
    bullet.is_enemy_bullet = True
    enemy_bullets.append(bullet)

def start_reload():
    global reloading, reload_timer
    if reloading:
        return
    if ammo_clip == max_clip:
        message_text.text = 'Магазин полон'
        return
    if ammo_reserve <= 0:
        message_text.text = 'Нет патронов!'
        return
    reloading = True
    reload_timer = reload_time
    update_ammo_ui(ammo_text, ammo_clip, ammo_reserve, reloading=True)
    if reload_sound:
        reload_sound.play()
    gun = weapons[active_weapon_index]
    gun.set_position(reload_gun_pos)
    invoke(lambda: gun.set_position(default_gun_pos), delay=reload_time)

def finish_reload():
    global ammo_clip, ammo_reserve, reloading
    needed = max_clip - ammo_clip
    if ammo_reserve >= needed:
        ammo_clip = max_clip
        ammo_reserve -= needed
    else:
        ammo_clip += ammo_reserve
        ammo_reserve = 0
    reloading = False
    update_ammo_ui(ammo_text, ammo_clip, ammo_reserve)
    message_text.text = ''

def fire_bullet():
    global ammo_clip, bullets, player, reloading, recoil_target
    if not player or game_over:
        return
    if reloading:
        return
    if ammo_clip <= 0:
        start_reload()
        return

    gun = weapons[active_weapon_index]
    recoil_target = Vec3(0, 0.05, -0.03) if not aiming else Vec3(0, 0.025, -0.015)
    gun.entity.position = default_gun_pos + recoil_target

    if gunshot_sound:
        gunshot_sound.play()

    ammo_clip -= 1
    update_ammo_ui(ammo_text, ammo_clip, ammo_reserve)

    if ammo_clip == 0 and ammo_reserve > 0:
        start_reload()

    start_pos = gun.get_world_barrel_pos()
    spread = 0.01 if aiming else 0.02
    dir_vec = camera.forward + Vec3(random.uniform(-spread, spread),
                                    random.uniform(-spread, spread),
                                    0)
    dir_vec = dir_vec.normalized()

    bullet = Entity(model='cube', color=color.red, scale=(0.05, 0.05, 0.2),
                    position=start_pos)
    bullet.look_at(start_pos + dir_vec)
    Entity(parent=bullet, model='sphere', color=color.white, scale=(0.1, 0.1, 0.1))
    bullet.velocity = dir_vec * 30
    bullet.lifetime = 1.0
    bullet.is_enemy_bullet = False
    bullets.append(bullet)

def spawn_health_packs(count=8):
    for _ in range(count):
        if not room_centers:
            break
        cx, cz = random.choice(room_centers)
        x = cx + random.uniform(-15, 15)
        z = cz + random.uniform(-15, 15)
        y = 0.5
        pack = Entity(
            position=(x, y, z),
            model='cube',
            color=color.red,
            scale=(1.2, 0.8, 1.2),
            collider='box'
        )
        Entity(parent=pack, model='cube', color=color.white,
               scale=(0.4, 0.08, 1.2), position=(0,0,0))
        Entity(parent=pack, model='cube', color=color.white,
               scale=(1.2, 0.08, 0.4), position=(0,0,0))
        health_packs.append(pack)

def start_wave(wave_index):
    global current_wave, wave_message_timer, game_over
    if wave_index >= len(waves):
        message_text.text = 'Поздравляем! Вы прошли все волны!'
        game_over = True
        return

    current_wave = wave_index
    wave = waves[wave_index]
    message_text.text = wave['label']
    wave_message_timer = 3.0

    for _ in range(wave['count']):
        enemy = spawn_enemy(room_centers, enemies,
                            health=wave['health'],
                            scale=wave['scale'],
                            color=wave['color'],
                            armed=True,
                            shoot_callback=create_enemy_bullet)
        if enemy:
            enemy.target = player
            enemy.shoot_sound = enemy_shot_sound

def start_game():
    global game_started, player, weapons, active_weapon_index, base_speed, player_health
    global health_text, message_text, ammo_text, enemies, game_over, bullets, enemy_bullets
    global last_damage_time, room_centers, health_packs, pickups, inventory
    global current_wave, wave_message_timer, exit_doors, ammo_clip, ammo_reserve, reloading
    global elevator, elevator_hint_text, current_fov, current_gun_pos

    print("start_game() вызвана")
    for obj in building_objects:
        destroy(obj)
    building_objects.clear()
    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    health_packs.clear()
    exit_doors.clear()
    room_centers.clear()
    for p in pickups:
        destroy(p)
    pickups.clear()
    inventory = [None, None, None]

    ammo_clip = 100
    ammo_reserve = 10000
    reloading = False
    current_fov = default_fov
    current_gun_pos = default_gun_pos

    try:
        destroy(menu_bg)
        destroy(logo)
        destroy(btn_start)
        destroy(btn_exit)

        if menu_music and menu_music.playing:
            menu_music.stop()
        if game_music and not game_music.playing:
            game_music.play()

        room_centers, exit_doors = generate_grid_rooms()
        print(f"Сгенерировано комнат: {len(room_centers)}")

        print("Создание игрока...")
        player, weapons, active_weapon_index, base_speed, player_health = create_player()
        inventory[0] = 0
        weapons[1].entity.visible = False
        weapons[0].entity.visible = True

        if room_centers:
            first_room = room_centers[0]
            player.position = (first_room[0] - 5, 0.6, first_room[1] - 5)
        else:
            player.position = (0, 0.6, 0)

        elevator_pos = getattr(settings, 'ELEVATOR_POSITION', (0, 0))
        elevator = Elevator(elevator_pos, floors=[0, -1])
        elevator.y = 0.0
        elevator.cabin.y = elevator.cabin.scale_y / 2
        elevator.door_progress = 1.0
        elevator.door_target = 1.0
        elevator.door_left.x = -elevator.cabin.scale_x/2 + 0.1
        elevator.door_right.x = elevator.cabin.scale_x/2 - 0.1

        elevator_hint_text = Text(text='Нажмите E, чтобы вызвать лифт', position=(0, -0.3), origin=(0,0), scale=1.5, color=color.white, enabled=False)

        print("Создание UI...")
        health_text, message_text = create_ui(player_health)
        ammo_text = create_ammo_ui(ammo_clip, ammo_reserve)

        print("Спавн аптечек...")
        spawn_health_packs(8)

        print("Спавн пикапов оружия...")
        spawn_weapon_pickups(settings.PICKUP_COUNT_PER_FLOOR)

        update_inventory_ui()

        enemies.clear()
        bullets.clear()
        enemy_bullets.clear()
        game_over = False
        last_damage_time = 0
        current_wave = 0
        wave_message_timer = 0

        start_wave(0)

        game_started = True
        print("Игра успешно запущена!")
    except Exception as e:
        print("!!! ОШИБКА В start_game():", e)
        import traceback
        traceback.print_exc()

btn_start.on_click = start_game
btn_exit.on_click = application.quit

# ---------- ОБНОВЛЕНИЕ ----------
def update():
    global player_health, game_over, last_damage_time, health_packs, fire_timer
    global current_wave, wave_message_timer, reloading, reload_timer
    global ammo_clip, ammo_reserve, ammo_text, enemy_bullets
    global current_fov, current_gun_pos, aiming
    global elevator, elevator_nearby, elevator_hint_text
    global recoil_target
    global pickups, inventory, weapons, active_weapon_index

    if not game_started or game_over:
        return

    gun = weapons[active_weapon_index]
    if reloading:
        target = reload_gun_pos
    elif aiming:
        target = aim_gun_pos
    else:
        target = default_gun_pos
    current_gun_pos = lerp(current_gun_pos, target + recoil_target, time.dt * recoil_speed)
    gun.entity.position = current_gun_pos
    recoil_target = lerp(recoil_target, Vec3(0,0,0), time.dt * recoil_speed * 0.8)

    # Подбор оружия
    for pickup in pickups[:]:
        if distance(player.position, pickup.position) < 1.5:
            free_slot = None
            for i, val in enumerate(inventory):
                if val is None:
                    free_slot = i
                    break
            if free_slot is not None:
                inventory[free_slot] = pickup.weapon_index
                weapons[pickup.weapon_index].entity.visible = False
                if free_slot == 0:
                    switch_weapon(0)
                destroy(pickup)
                pickups.remove(pickup)
                update_inventory_ui()
                message_text.text = 'Оружие подобрано!'
                invoke(lambda: setattr(message_text, 'text', ''), delay=1)
            else:
                inventory[active_weapon_index] = pickup.weapon_index
                switch_weapon(active_weapon_index)
                destroy(pickup)
                pickups.remove(pickup)
                update_inventory_ui()
                message_text.text = 'Оружие заменено!'
                invoke(lambda: setattr(message_text, 'text', ''), delay=1)

    if elevator and player:
        dist = distance(player.position, Vec3(elevator.position[0], player.y, elevator.position[1]))
        if dist < 3.0:
            elevator_nearby = True
            if elevator_hint_text:
                elevator_hint_text.enabled = True
        else:
            elevator_nearby = False
            if elevator_hint_text:
                elevator_hint_text.enabled = False

    if elevator:
        elevator.update()

    if player:
        if player.y < -WALL_HEIGHT - 2:
            player.position = (player.x, -WALL_HEIGHT + 0.6, player.z)
            player.velocity = Vec3(0, 0, 0)
            player.grounded = True
            message_text.text = 'Вы провалились в подвал!'

    target_fov = aim_fov if aiming else default_fov
    current_fov = lerp(current_fov, target_fov, time.dt * aim_speed)
    camera.fov = current_fov

    if reloading:
        reload_timer -= time.dt
        if reload_timer <= 0:
            finish_reload()

    if held_keys['shift']:
        player.speed = base_speed * 3
    else:
        player.speed = base_speed

    if held_keys['control']:
        player.height = 0.9
        player.camera_pivot.position.y = 0.5
    else:
        player.height = 1.8
        player.camera_pivot.position.y = 1.5

    if mouse.left and not game_over:
        fire_timer += time.dt
        if fire_timer >= fire_interval:
            fire_timer = 0
            fire_bullet()
    else:
        fire_timer = 0

    if wave_message_timer > 0:
        wave_message_timer -= time.dt
        if wave_message_timer <= 0:
            message_text.text = ''

    # ---------- ПУЛИ ИГРОКА ----------
    for bullet in bullets[:]:
        bullet.position += bullet.velocity * time.dt
        bullet.lifetime -= time.dt

        hit_info = bullet.intersects(ignore=(player, bullet))
        if hit_info.hit and hit_info.entity in building_objects:
            destroy(bullet)
            bullets.remove(bullet)
            continue

        hit = False
        for enemy_data in enemies[:]:
            enemy_entity = enemy_data['entity']
            if not enemy_entity.enabled:
                continue
            if distance(bullet.position, enemy_entity.position) < 0.8:
                if enemy_entity.take_damage(1):
                    if hit_sound:
                        hit_sound.play()
                    enemies.remove(enemy_data)
                hit = True
                break
        if hit or bullet.lifetime <= 0:
            if bullet in bullets:
                destroy(bullet)
                bullets.remove(bullet)

    # ---------- ПУЛИ ВРАГОВ ----------
    for bullet in enemy_bullets[:]:
        bullet.position += bullet.direction * bullet.speed * time.dt
        bullet.lifetime -= time.dt

        hit_info = bullet.intersects(ignore=(bullet,))
        if hit_info.hit and hit_info.entity in building_objects:
            destroy(bullet)
            enemy_bullets.remove(bullet)
            continue

        if distance(bullet.position, player.position) < 0.8:
            player_health -= 5
            health_text.text = f'Health: {player_health}'
            destroy(bullet)
            enemy_bullets.remove(bullet)
            if player_health <= 0:
                player_health = 0
                message_text.text = 'Игра окончена'
                game_over = True
            continue

        if bullet.lifetime <= 0:
            destroy(bullet)
            enemy_bullets.remove(bullet)

    # ---------- ПРОВЕРКА ОКОНЧАНИЯ ВОЛНЫ ----------
    if len(enemies) == 0 and not game_over:
        if current_wave + 1 < len(waves):
            start_wave(current_wave + 1)
        else:
            message_text.text = 'Поздравляем! Вы прошли все волны!'
            game_over = True

    # ---------- УРОН ИГРОКУ (ближний бой) ----------
    for enemy_data in enemies:
        enemy_entity = enemy_data['entity']
        if not enemy_entity.enabled:
            continue
        if distance(enemy_entity.position, player.position) < 1.5:
            if time.time() - last_damage_time > damage_cooldown:
                damage = 5
                player_health -= damage
                last_damage_time = time.time()
                if player_health <= 0:
                    player_health = 0
                    message_text.text = 'Игра окончена'
                    game_over = True
                health_text.text = f'Health: {player_health}'

    # ---------- АПТЕЧКИ ----------
    for pack in health_packs[:]:
        if not pack.enabled:
            continue
        if distance(player.position, pack.position) < 1.5:
            player_health = min(player_health + 30, settings.PLAYER_MAX_HEALTH)
            health_text.text = f'Health: {player_health}'
            destroy(pack)
            health_packs.remove(pack)

    health_text.text = f'Health: {player_health}'
    if not reloading:
        update_ammo_ui(ammo_text, ammo_clip, ammo_reserve)
    else:
        update_ammo_ui(ammo_text, ammo_clip, ammo_reserve, reloading=True)

# ---------- ВВОД ----------
def input(key):
    global aiming
    global elevator, elevator_nearby
    global active_weapon_index

    if key == 'escape':
        application.quit()

    if not game_started:
        return

    if key == 'right mouse down':
        aiming = True
    if key == 'right mouse up':
        aiming = False

    if key == 'r':
        start_reload()

    if key == 'left mouse down' and not game_over:
        fire_bullet()
        fire_timer = 0

    # ---------- ПЕРЕКЛЮЧЕНИЕ ОРУЖИЯ КОЛЁСИКОМ ----------
    if key == 'scroll up':
        next_idx = active_weapon_index
        for i in range(1, 3):
            test = (active_weapon_index + i) % 3
            if inventory[test] is not None:
                next_idx = test
                break
        if next_idx != active_weapon_index:
            switch_weapon(next_idx)

    if key == 'scroll down':
        prev_idx = active_weapon_index
        for i in range(1, 3):
            test = (active_weapon_index - i) % 3
            if inventory[test] is not None:
                prev_idx = test
                break
        if prev_idx != active_weapon_index:
            switch_weapon(prev_idx)

    # ---------- ВЫЗОВ ЛИФТА ----------
    if key == 'e':
        if elevator and elevator_nearby:
            floor_index = 0 if player.y > -3 else 1
            if elevator.current_floor == floor_index:
                elevator.toggle_doors()
            else:
                elevator.call(floor_index)

    if key == 'y':
        if elevator:
            ray_origin = camera.position
            ray_direction = camera.forward
            hit_info = raycast(ray_origin, ray_direction, distance=20, ignore=[player])
            if hit_info.hit:
                for btn in elevator.call_buttons:
                    if hit_info.entity == btn:
                        floor_idx = btn.floor_index
                        elevator.call(floor_idx)
                        break

    if key == 'page up':
        if elevator:
            elevator.call(0)
    if key == 'page down':
        if elevator:
            elevator.call(1)

AmbientLight(color=color.rgb(150, 150, 150), intensity=0.5)
app.run()