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

app = Ursina(borderless=False)

# ------------------ ЗВУКИ И МУЗЫКА ------------------
try:
    gunshot_sound = Audio(settings.SOUND_GUNSHOT, loop=False, autoplay=False)
    enemy_shot_sound = Audio(settings.SOUND_ENEMY_SHOT, loop=False, autoplay=False)
    hit_sound = Audio(settings.SOUND_HIT, loop=False, autoplay=False)
    menu_click_sound = Audio(settings.SOUND_MENU_CLICK, loop=False, autoplay=False)
    menu_music = Audio(settings.SOUND_MENU_MUSIC, loop=True, autoplay=False)
    game_music = Audio(settings.SOUND_GAME_MUSIC, loop=True, autoplay=False)
except:
    gunshot_sound = None
    enemy_shot_sound = None
    hit_sound = None
    menu_click_sound = None
    menu_music = None
    game_music = None
    print("Звуки не найдены, будут без звука.")

# Запускаем музыку меню при старте
if menu_music:
    menu_music.play()

# ---------- ФУНКЦИЯ ДЛЯ КЛИКА С ПАУЗОЙ МУЗЫКИ ----------
def play_click_and_pause_music():
    """Останавливает музыку меню, проигрывает клик, затем возобновляет музыку."""
    if menu_music and menu_music.playing:
        menu_music.stop()
        if menu_click_sound:
            menu_click_sound.play()
        # Возобновить музыку через 0.2 секунды
        invoke(lambda: menu_music.play() if menu_music else None, delay=0.2)
    else:
        if menu_click_sound:
            menu_click_sound.play()

# ------------------ ГЛАВНОЕ МЕНЮ ------------------
menu_bg = Entity(model='quad', scale=(2, 1), color=color.black, z=1)
title_text = Text(text='CUPER', position=(0, 0.2), origin=(0,0), scale=5, color=color.white)

def on_start_click():
    play_click_and_pause_music()
    # Небольшая задержка, чтобы звук успел проиграться
    invoke(start_game, delay=0.1)

def on_exit_click():
    play_click_and_pause_music()
    invoke(application.quit, delay=0.2)

btn_start = Button(text='Новая игра', scale=(0.3, 0.1), position=(0, -0.1), color=color.azure, on_click=on_start_click)
btn_exit = Button(text='Выход', scale=(0.3, 0.1), position=(0, -0.25), color=color.red, on_click=on_exit_click)

game_started = False

# Глобальные игровые переменные
player = None
gun = None
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
    {'count': 20, 'health': 1,   'scale': 1,   'color': color.red,     'armed_count': 2, 'label': 'Волна 1: Обычные враги'},
    {'count': 10, 'health': 10,  'scale': 2,   'color': color.magenta, 'armed_count': 2, 'label': 'Волна 2: Боссы'},
    {'count': 5,  'health': 25,  'scale': 4,   'color': color.gold,    'armed_count': 2, 'label': 'Волна 3: Мегабоссы'},
]
wave_message_timer = 0

# ---------- ПЕРЕМЕННЫЕ ДЛЯ ПРИЦЕЛИВАНИЯ ----------
aiming = False
default_fov = 90
aim_fov = 60
default_gun_pos = Vec3(0.3, -0.2, 0.5)
aim_gun_pos = Vec3(0.0, -0.05, 0.25)
reload_gun_pos = Vec3(0.2, -0.5, 0.2)
current_gun_pos = default_gun_pos
current_fov = default_fov
aim_speed = 8.0

# Переменные для стрельбы очередью
fire_timer = 0
fire_interval = 1 / settings.FIRE_RATE

# ---------- ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ПУЛЬ ВРАГОВ ----------
def create_enemy_bullet(start_pos, direction, damage=1):
    bullet = Entity(model='sphere', color=color.blue, scale=0.1,
                    position=start_pos, collider='sphere')
    bullet.direction = direction
    bullet.speed = 15
    bullet.lifetime = 3.0
    bullet.damage = damage
    bullet.is_enemy_bullet = True
    enemy_bullets.append(bullet)

# ---------- ФУНКЦИЯ ПЕРЕЗАРЯДКИ ----------
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

# ---------- ФУНКЦИЯ СОЗДАНИЯ ПУЛИ ИГРОКА ----------
def fire_bullet():
    global ammo_clip, bullets, player, gun, gunshot_sound, reloading
    if not player or game_over:
        return
    if reloading:
        return
    if ammo_clip <= 0:
        start_reload()
        return

    gun.position = (0.3, -0.2, 0.3)
    invoke(setattr, gun, 'position', (0.3, -0.2, 0.5), delay=0.1)

    if gunshot_sound:
        gunshot_sound.play()

    ammo_clip -= 1
    update_ammo_ui(ammo_text, ammo_clip, ammo_reserve)

    if ammo_clip == 0 and ammo_reserve > 0:
        start_reload()

    if hasattr(gun, 'barrel_tip'):
        start_pos = gun.barrel_tip.world_position
    else:
        start_pos = player.position + player.forward * 0.8 + Vec3(0, 0.2, 0)

    spread = 0.02
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

# ---------- ФУНКЦИЯ ДЛЯ СОЗДАНИЯ АПТЕЧЕК ----------
def spawn_health_packs(count=10):
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
            scale=(0.3, 0.2, 0.3),
            collider='box'
        )
        Entity(parent=pack, model='cube', color=color.white,
               scale=(0.1, 0.02, 0.3), position=(0,0,0))
        Entity(parent=pack, model='cube', color=color.white,
               scale=(0.3, 0.02, 0.1), position=(0,0,0))
        health_packs.append(pack)

# ---------- ФУНКЦИЯ ЗАПУСКА ВОЛНЫ ----------
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

    armed_count = wave.get('armed_count', 0)
    for i in range(wave['count']):
        armed = (i < armed_count)
        enemy = spawn_enemy(room_centers, enemies,
                            health=wave['health'],
                            scale=wave['scale'],
                            color=wave['color'],
                            armed=armed,
                            shoot_callback=create_enemy_bullet)
        if enemy:
            enemy.target = player
            enemy.shoot_sound = enemy_shot_sound

# ---------- СТАРТ ИГРЫ ----------
def start_game():
    global game_started, player, gun, base_speed, player_health, health_text, message_text
    global enemies, game_over, bullets, enemy_bullets, last_damage_time, room_centers, health_packs
    global current_wave, wave_message_timer, exit_doors, ammo_clip, ammo_reserve, reloading
    global ammo_text
    global current_fov, current_gun_pos

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

    ammo_clip = 100
    ammo_reserve = 10000
    reloading = False

    current_fov = default_fov
    current_gun_pos = default_gun_pos

    try:
        destroy(menu_bg)
        destroy(title_text)
        destroy(btn_start)
        destroy(btn_exit)

        # Переключение музыки
        if menu_music and menu_music.playing:
            menu_music.stop()
        if game_music and not game_music.playing:
            game_music.play()

        room_centers, exit_doors = generate_grid_rooms()
        print("Сетка комнат создана, центров:", len(room_centers))
        print("Выходов:", len(exit_doors))

        print("Создание игрока...")
        player, gun, base_speed, player_health = create_player()
        player.position = (0, 0.6, 0)
        print("Игрок создан")

        print("Создание UI...")
        health_text, message_text = create_ui(player_health)
        ammo_text = create_ammo_ui(ammo_clip, ammo_reserve)
        print("UI создан")

        print("Спавн аптечек...")
        spawn_health_packs(12)
        print("Аптечки созданы")

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

# ---------- ОБНОВЛЕНИЕ ----------
def update():
    global player_health, game_over, last_damage_time, health_packs, fire_timer
    global current_wave, wave_message_timer, reloading, reload_timer
    global ammo_clip, ammo_reserve, ammo_text, enemy_bullets
    global current_fov, current_gun_pos, aiming

    if not game_started or game_over:
        return

    # ---------- АНИМАЦИЯ ОРУЖИЯ ----------
    if reloading:
        target_gun_pos = reload_gun_pos
    elif aiming:
        target_gun_pos = aim_gun_pos
    else:
        target_gun_pos = default_gun_pos

    current_gun_pos = lerp(current_gun_pos, target_gun_pos, time.dt * aim_speed)
    if gun:
        gun.position = current_gun_pos

    target_fov = aim_fov if aiming else default_fov
    current_fov = lerp(current_fov, target_fov, time.dt * aim_speed)
    camera.fov = current_fov

    # Перезарядка
    if reloading:
        reload_timer -= time.dt
        if reload_timer <= 0:
            finish_reload()

    # Бег
    if held_keys['shift']:
        player.speed = base_speed * 3
    else:
        player.speed = base_speed

    # Приседание
    if held_keys['control']:
        player.height = 0.9
        player.camera_pivot.position.y = 0.5
    else:
        player.height = 1.8
        player.camera_pivot.position.y = 1.5

    # Стрельба
    if mouse.left and not game_over:
        fire_timer += time.dt
        if fire_timer >= fire_interval:
            fire_timer = 0
            fire_bullet()
    else:
        fire_timer = 0

    # Таймер сообщения о волне
    if wave_message_timer > 0:
        wave_message_timer -= time.dt
        if wave_message_timer <= 0:
            message_text.text = ''

    # ---------- ПУЛИ ИГРОКА ----------
    for bullet in bullets[:]:
        bullet.position += bullet.velocity * time.dt
        bullet.lifetime -= time.dt
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
        if bullet.lifetime <= 0:
            destroy(bullet)
            enemy_bullets.remove(bullet)
            continue
        if distance(bullet.position, player.position) < 0.8:
            player_health -= bullet.damage
            health_text.text = f'Health: {player_health}'
            destroy(bullet)
            enemy_bullets.remove(bullet)
            if player_health <= 0:
                player_health = 0
                message_text.text = 'Игра окончена'
                game_over = True
            continue

    # ---------- ПРОВЕРКА ОКОНЧАНИЯ ВОЛНЫ ----------
    if len(enemies) == 0 and not game_over:
        if current_wave + 1 < len(waves):
            start_wave(current_wave + 1)
        else:
            message_text.text = 'Поздравляем! Вы прошли все волны!'
            game_over = True

    # ---------- УРОН ИГРОКУ ----------
    for enemy_data in enemies:
        enemy_entity = enemy_data['entity']
        if not enemy_entity.enabled:
            continue
        if distance(enemy_entity.position, player.position) < 1.5:
            if time.time() - last_damage_time > damage_cooldown:
                damage = 10
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
        if distance(player.position, pack.position) < 0.8:
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

AmbientLight(color=color.rgb(50, 50, 50))
app.run()