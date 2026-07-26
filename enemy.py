# enemy.py
from ursina import *
import random
import time

def create_enemy_body(pos, scale_factor=1.0, body_color=color.red):
    body = Entity(position=pos, scale=scale_factor)
    Entity(parent=body, model='cube', color=body_color, scale=(0.6, 0.8, 0.4), position=(0, 0.9, 0))
    Entity(parent=body, model='sphere', color=color.peach, scale=(0.5, 0.5, 0.5), position=(0, 1.6, 0))
    Entity(parent=body, model='cube', color=color.orange, scale=(0.2, 0.7, 0.2), position=(-0.4, 0.8, 0))
    Entity(parent=body, model='cube', color=color.orange, scale=(0.2, 0.7, 0.2), position=(0.4, 0.8, 0))
    Entity(parent=body, model='cube', color=color.brown, scale=(0.25, 0.8, 0.25), position=(-0.2, 0.1, 0))
    Entity(parent=body, model='cube', color=color.brown, scale=(0.25, 0.8, 0.25), position=(0.2, 0.1, 0))
    return body

def spawn_enemy(room_centers, enemies, is_boss=False):
    if not room_centers:
        return
    cx, cz = random.choice(room_centers)
    x = cx + random.uniform(-18, 18)
    z = cz + random.uniform(-18, 18)
    if is_boss:
        scale = 2.0
        health = 5
        body_color = color.magenta
    else:
        scale = 1.0
        health = 1
        body_color = color.red
    enemy_entity = create_enemy_body((x, 0, z), scale_factor=scale, body_color=body_color)
    enemies.append({'entity': enemy_entity, 'health': health, 'is_boss': is_boss})

def spawn_explosion(pos):
    for _ in range(10):
        p = Entity(model='cube', color=color.red, scale=0.1, position=pos, rotation=random.random()*360)
        p.velocity = (Vec3(random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)).normalized()
                      * random.uniform(3,6))
        destroy(p, delay=0.3)
    try:
        Audio('shot_echo', loop=False, autoplay=True)
    except:
        pass