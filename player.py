# player.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from settings import PLAYER_MAX_HEALTH

def create_player():
    player = FirstPersonController()
    player.position = (0, 1, 0)
    base_speed = 10
    player_health = PLAYER_MAX_HEALTH

    # ---------- ДЕТАЛИЗИРОВАННЫЙ АВТОМАТ ----------
    gun = Entity(parent=camera, position=(0.3, -0.2, 0.5))

    # Корпус (ствольная коробка)
    receiver = Entity(parent=gun, model='cube', color=color.dark_gray,
                      scale=(0.18, 0.10, 0.35), position=(0, 0, 0.05))
    # Ствол (основной)
    barrel_base = Entity(parent=gun, model='cylinder', color=color.gray,
                         scale=(0.04, 0.35, 0.04), position=(0, 0, 0.28), rotation=(90, 0, 0))
    # Дуло (кончик ствола, сужается)
    barrel_tip = Entity(parent=gun, model='cylinder', color=color.dark_gray,
                        scale=(0.025, 0.08, 0.025), position=(0, 0, 0.45), rotation=(90, 0, 0))
    # Сохраняем ссылку на дуло для выстрелов
    gun.barrel_tip = barrel_tip

    # Цевьё (нижняя часть ствола)
    handguard = Entity(parent=gun, model='cube', color=color.brown,
                       scale=(0.06, 0.05, 0.20), position=(0, -0.03, 0.25))
    # Приклад
    stock = Entity(parent=gun, model='cube', color=color.brown,
                   scale=(0.12, 0.04, 0.20), position=(-0.06, 0, -0.18))
    stock.rotation_x = -5   # небольшой наклон
    # Рукоятка
    grip = Entity(parent=gun, model='cube', color=color.black,
                  scale=(0.05, 0.12, 0.06), position=(0, -0.08, -0.02))
    # Магазин (изогнутый)
    mag = Entity(parent=gun, model='cylinder', color=color.dark_gray,
                 scale=(0.04, 0.14, 0.04), position=(0, -0.07, 0.18))
    mag.rotation_x = -10
    # Целик и мушка
    rear_sight = Entity(parent=gun, model='cube', color=color.black,
                        scale=(0.02, 0.02, 0.01), position=(0, 0.06, 0.08))
    front_sight = Entity(parent=gun, model='cube', color=color.black,
                         scale=(0.02, 0.03, 0.01), position=(0, 0.06, 0.35))
    # Дульный тормоз
    muzzle = Entity(parent=gun, model='cube', color=color.dark_gray,
                    scale=(0.035, 0.035, 0.04), position=(0, 0, 0.49))
    # Крышка ствольной коробки
    top_cover = Entity(parent=gun, model='cube', color=color.dark_gray,
                       scale=(0.10, 0.015, 0.20), position=(0, 0.055, 0.05))

    return player, gun, base_speed, player_health