# enemy.py
from ursina import *
import math
import random
from settings import *

class Enemy(Entity):
    def __init__(self, position, is_boss=False, texture=None):
        # Простой куб ярко-красного цвета
        super().__init__(
            position=position,
            model='cube',
            color=color.red,
            scale=(1, 1.5, 1),  # высокий, чтобы было видно
            collider='box'
        )
        self.is_boss = is_boss
        self.health = 5 if is_boss else 1
        self.walk_cycle = 0.0
        self.jump_timer = 0.0
        self.velocity = Vec3(0,0,0)
        self.gravity = -20
        self.grounded = True
        self.target = None
        # Для босса сделаем больше и другого цвета
        if is_boss:
            self.scale = (2, 3, 2)
            self.color = color.magenta

    def update(self):
        if not self.target:
            return

        dir_to_target = self.target.position - self.position
        dir_to_target.y = 0
        dist = dir_to_target.length()

        if dist > 0.5:
            move_vec = dir_to_target.normalized() * ENEMY_WALK_SPEED * time.dt
            self.position += move_vec
            # Поворот
            if dist > 0.1:
                self.look_at(Vec3(self.target.position.x, self.position.y, self.target.position.z))

        # Прыжки
        self.jump_timer += time.dt
        if self.jump_timer >= ENEMY_JUMP_INTERVAL and self.grounded:
            self.jump_timer = 0
            self.velocity.y = ENEMY_JUMP_HEIGHT * 5
            self.grounded = False

        if not self.grounded:
            self.velocity.y += self.gravity * time.dt
            self.position += self.velocity * time.dt
            if self.position.y <= 0:
                self.position.y = 0
                self.velocity.y = 0
                self.grounded = True

    def take_damage(self, damage):
        self.health -= damage
        spawn_explosion(self.position)
        if self.health <= 0:
            destroy(self)
            return True
        return False

def spawn_enemy(room_centers, enemies, is_boss=False):
    if not room_centers:
        return None
    cx, cz = random.choice(room_centers)
    x = cx + random.uniform(-18, 18)
    z = cz + random.uniform(-18, 18)
    enemy = Enemy(position=(x, 0.5, z), is_boss=is_boss)  # поднимем чуть выше
    enemies.append({'entity': enemy, 'health': enemy.health, 'is_boss': is_boss})
    return enemy

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