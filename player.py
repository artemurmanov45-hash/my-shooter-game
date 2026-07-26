# player.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from settings import PLAYER_MAX_HEALTH

def create_player():
    player = FirstPersonController()
    player.position = (0, 1, 0)
    base_speed = 10
    player_health = PLAYER_MAX_HEALTH

    gun = Entity(parent=camera, model='cube', color=color.dark_gray,
                 scale=(0.2, 0.1, 0.5), position=(0.3, -0.2, 0.5))
    Entity(parent=gun, model='cube', color=color.black,
           scale=(0.1, 0.08, 0.2), position=(0, 0, 0.35))
    Entity(parent=gun, model='cube', color=color.brown,
           scale=(0.12, 0.2, 0.1), position=(0, -0.15, -0.1))

    return player, gun, base_speed, player_health