# main.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time
import sys
import os   # <-- добавили для получения текущей директории

import settings
from room import generate_rooms
from player import create_player
from ui import create_ui
from enemy import spawn_enemy, spawn_explosion

# ------------------ ДИАГНОСТИКА ------------------
print("=== НАЧАЛО СКРИПТА ===")
print("Текущая директория:", os.getcwd())
print("Интерпретатор Python:", sys.executable)
print("Аргументы командной строки:", sys.argv)
print("Версия Python:", sys.version)
print("==========================================")

app = Ursina(borderless=False)

# ------------------ ГЛАВНОЕ МЕНЮ ------------------
menu_bg = Entity(model='quad', scale=(2, 1), color=color.black, z=1)
title_text = Text(text='CUPER', position=(0, 0.2), origin=(0,0), scale=5, color=color.white)
btn_start = Button(text='Новая игра', scale=(0.3, 0.1), position=(0, -0.1), color=color.azure)
btn_exit = Button(text='Выход', scale=(0.3, 0.1), position=(0, -0.25), color=color.red)

game_started = False

# Глобальные игровые переменные
player = None
gun = None
base_speed = 10
player_health = settings.PLAYER_MAX_HEALTH
health_text = None
message_text = None
enemies = []
boss_spawned = False
game_over = False
bullets = []
last_damage_time = 0
damage_cooldown = 1.0
room_centers = []

def start_game():
    global game_started, player, gun, base_speed, player_health, health_text, message_text
    global enemies, boss_spawned, game_over, bullets, last_damage_time, room_centers

    print("start_game() вызвана")   # <-- диагностика

    try:
        # Убираем меню
        destroy(menu_bg)
        destroy(title_text)
        destroy(btn_start)
        destroy(btn_exit)

        # Генерация мира
        print("Генерация комнат...")
        room_centers = generate_rooms()
        print("Комнаты созданы, центров:", len(room_centers))

        print("Создание игрока...")
        player, gun, base_speed, player_health = create_player()
        print("Игрок создан")

        print("Создание UI...")
        health_text, message_text = create_ui(player_health)
        print("UI создан")

        # Враги
        print("Спавн 20 врагов...")
        for _ in range(20):
            spawn_enemy(room_centers, enemies, is_boss=False)
        print("Враги созданы")

        boss_spawned = False
        game_over = False
        bullets.clear()
        last_damage_time = 0

        game_started = True
        print("Игра успешно запущена!")
    except Exception as e:
        print("!!! ОШИБКА В start_game():", e)
        import traceback
        traceback.print_exc()
        # Чтобы окно не закрылось сразу, можно оставить сообщение
        # Но лучше дать возможность увидеть ошибку в консоли.

btn_start.on_click = start_game
btn_exit.on_click = application.quit

def update():
    global player_health, boss_spawned, game_over, last_damage_time

    if not game_started or game_over:
        return

    # Бег
    if held_keys['shift']:
        player.speed = base_speed * 3
    else:
        player.speed = base_speed

    # Пули
    for bullet in bullets[:]:
        bullet.position += bullet.velocity * time.dt
        bullet.lifetime -= time.dt
        hit = False
        for enemy_data in enemies[:]:
            enemy_entity = enemy_data['entity']
            if distance(bullet.position, enemy_entity.position) < 0.8:
                enemy_data['health'] -= 1
                spawn_explosion(enemy_entity.position)
                if enemy_data['health'] <= 0:
                    destroy(enemy_entity)
                    enemies.remove(enemy_data)
                    if enemy_data['is_boss']:
                        message_text.text = 'Игра пройдена!'
                        game_over = True
                    else:
                        if not boss_spawned and len(enemies) == 0:
                            spawn_enemy(room_centers, enemies, is_boss=True)
                            boss_spawned = True
                hit = True
                break
        if hit or bullet.lifetime <= 0:
            if bullet in bullets:
                destroy(bullet)
                bullets.remove(bullet)

    # Движение врагов и урон
    for enemy_data in enemies:
        enemy_entity = enemy_data['entity']
        dir_to_player = player.position - enemy_entity.position
        dir_to_player.y = 0
        if dir_to_player.length() > 0.5:
            enemy_entity.position += dir_to_player.normalized() * time.dt * 3.0

        if distance(enemy_entity.position, player.position) < 1.5:
            if time.time() - last_damage_time > damage_cooldown:
                if enemy_data['is_boss']:
                    damage = 30
                else:
                    damage = 10
                player_health -= damage
                last_damage_time = time.time()
                if player_health <= 0:
                    player_health = 0
                    message_text.text = 'Игра окончена'
                    game_over = True
                health_text.text = f'Health: {player_health}'

    health_text.text = f'Health: {player_health}'

def input(key):
    if key == 'escape':
        application.quit()

    if not game_started:
        return

    if key == 'left mouse down' and not game_over:
        # Отдача оружия
        gun.position = (0.3, -0.2, 0.3)
        invoke(setattr, gun, 'position', (0.3, -0.2, 0.5), delay=0.1)
        # Создание пули
        start_pos = player.position + player.forward * 0.8 + Vec3(0, 0.2, 0)
        bullet = Entity(model='cube', color=color.yellow, scale=(0.05, 0.05, 0.2),
                        position=start_pos, rotation=player.rotation)
        Entity(parent=bullet, model='sphere', color=color.white, scale=(0.1, 0.1, 0.1))
        bullet.velocity = player.forward * 30
        bullet.lifetime = 1.0
        bullets.append(bullet)

AmbientLight(color=color.rgb(50, 50, 50))
app.run()