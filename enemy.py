from ursina import *
import math
import random
from settings import *

class Enemy(Entity):
    def __init__(self, position, health=1, scale=1, body_color=color.red, armed=False, shoot_callback=None):
        super().__init__(
            position=position,
            model='cube',
            color=color.clear,
            scale=(1, 1, 1),
            collider='box'
        )
        self.health = health
        self.armed = armed
        self.shoot_callback = shoot_callback
        self.shoot_sound = None  # <-- добавлено для звука выстрела врага
        self.shoot_timer = 0
        self.shoot_interval = 0.5
        self.shoot_range = 20
        self.damage_per_shot = 1
        self.walk_cycle = 0.0
        self.jump_timer = 0.0
        self.velocity = Vec3(0, 0, 0)
        self.gravity = -20
        self.grounded = True
        self.target = None

        s = scale
        if armed:
            body_color = color.orange

        # ----- Тело -----
        self.torso = Entity(parent=self, model='cube', color=body_color,
                            scale=(0.6*s, 0.7*s, 0.4*s), position=(0, 0.9*s, 0))
        self.head = Entity(parent=self, model='sphere', color=color.peach,
                           scale=(0.35*s, 0.35*s, 0.35*s), position=(0, 1.7*s, 0))
        # Глаза
        eye_offset = 0.15*s
        eye_z = 0.2*s
        Entity(parent=self.head, model='sphere', color=color.white,
               scale=(0.08*s, 0.08*s, 0.04*s), position=(eye_offset, 0.1*s, eye_z))
        Entity(parent=self.head, model='sphere', color=color.white,
               scale=(0.08*s, 0.08*s, 0.04*s), position=(-eye_offset, 0.1*s, eye_z))
        Entity(parent=self.head, model='sphere', color=color.black,
               scale=(0.04*s, 0.04*s, 0.04*s), position=(eye_offset+0.02*s, 0.1*s, eye_z+0.02*s))
        Entity(parent=self.head, model='sphere', color=color.black,
               scale=(0.04*s, 0.04*s, 0.04*s), position=(-eye_offset+0.02*s, 0.1*s, eye_z+0.02*s))
        # Руки
        self.arm_l = Entity(parent=self, model='cube', color=color.orange,
                            scale=(0.15*s, 0.6*s, 0.15*s), position=(-0.5*s, 0.9*s, 0))
        self.arm_r = Entity(parent=self, model='cube', color=color.orange,
                            scale=(0.15*s, 0.6*s, 0.15*s), position=(0.5*s, 0.9*s, 0))
        # Ноги
        self.leg_l = Entity(parent=self, model='cube', color=color.brown,
                            scale=(0.2*s, 0.6*s, 0.2*s), position=(-0.25*s, 0.2*s, 0))
        self.leg_r = Entity(parent=self, model='cube', color=color.brown,
                            scale=(0.2*s, 0.6*s, 0.2*s), position=(0.25*s, 0.2*s, 0))
        # Коллайдер
        self.collider = BoxCollider(self, center=(0, 0.9*s, 0), size=(0.6*s, 1.2*s, 0.5*s))

    def update(self):
        if not self.target:
            return

        dir_to_target = self.target.position - self.position
        dist = dir_to_target.length()
        dir_to_target.y = 0

        # Движение
        if dist > 0.5 and dist > self.shoot_range * 0.8:
            move_vec = dir_to_target.normalized() * ENEMY_WALK_SPEED * time.dt
            self.position += move_vec
            self.walk_cycle += time.dt * 8
            swing = math.sin(self.walk_cycle) * 0.4
            self.arm_l.rotation_z = -swing
            self.arm_r.rotation_z = swing
            self.leg_l.rotation_z = swing
            self.leg_r.rotation_z = -swing
            if dist > 0.1:
                self.look_at(Vec3(self.target.position.x, self.position.y, self.target.position.z))
        else:
            if dist > 0.5:
                move_vec = dir_to_target.normalized() * ENEMY_WALK_SPEED * 0.3 * time.dt
                self.position += move_vec
            self.arm_l.rotation_z = 0
            self.arm_r.rotation_z = 0
            self.leg_l.rotation_z = 0
            self.leg_r.rotation_z = 0

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

        # ----- СТРЕЛЬБА С ЗВУКОМ -----
        if self.armed and self.shoot_callback and self.target:
            if dist < self.shoot_range:
                self.shoot_timer += time.dt
                if self.shoot_timer >= self.shoot_interval:
                    self.shoot_timer = 0
                    dir_to_player = (self.target.position - self.position).normalized()
                    spread = 0.05
                    dir_with_spread = dir_to_player + Vec3(random.uniform(-spread, spread),
                                                           random.uniform(-spread, spread),
                                                           random.uniform(-spread, spread))
                    dir_with_spread = dir_with_spread.normalized()
                    start_pos = self.position + Vec3(0, 0.5, 0)
                    self.shoot_callback(start_pos, dir_with_spread, self.damage_per_shot)
                    # <-- ДОБАВЛЕНО: звук выстрела врага
                    if self.shoot_sound:
                        self.shoot_sound.play()

    def take_damage(self, damage):
        self.health -= damage
        spawn_explosion(self.position)
        if self.health <= 0:
            destroy(self)
            return True
        return False

def spawn_enemy(room_centers, enemies, health=1, scale=1, color=color.red, armed=False, shoot_callback=None):
    if not room_centers:
        return None
    cx, cz = random.choice(room_centers)
    x = cx + random.uniform(-18, 18)
    z = cz + random.uniform(-18, 18)
    enemy = Enemy(position=(x, 0, z), health=health, scale=scale,
                  body_color=color, armed=armed, shoot_callback=shoot_callback)
    enemies.append({'entity': enemy, 'health': health})
    return enemy

def spawn_explosion(pos):
    for _ in range(10):
        p = Entity(model='cube', color=color.red, scale=0.1, position=pos, rotation=random.random()*360)
        p.velocity = (Vec3(random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)).normalized() * random.uniform(3,6))
        destroy(p, delay=0.3)
    try:
        Audio('shot_echo', loop=False, autoplay=True)
    except:
        pass