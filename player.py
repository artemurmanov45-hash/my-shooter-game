
# player.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from settings import PLAYER_MAX_HEALTH
import settings
import os

class Weapon3D:
    def __init__(self, parent, model_path, position=(0.3, -0.2, 0.5), scale=0.5):
        self.parent = parent
        self.position = position
        self.scale = scale
        self.model_path = model_path

        if os.path.exists(model_path):
            try:
                self.entity = Entity(
                    parent=parent,
                    model=model_path,
                    position=position,
                    scale=scale,
                    rotation=(0, 0, 0),
                    collider=None
                )
                print(f"[Weapon3D] Модель '{model_path}' загружена.")
            except Exception as e:
                print(f"[Weapon3D] Ошибка: {e}. Заглушка.")
                self._create_fallback(parent, position)
        else:
            print(f"[Weapon3D] Файл '{model_path}' не найден. Заглушка.")
            self._create_fallback(parent, position)

        self.barrel_tip = self._find_barrel_tip(self.entity)
        if not self.barrel_tip:
            self.barrel_tip = Entity(parent=self.entity, position=(0, 0, 0.4))
            print("[Weapon3D] Дуло создано по умолчанию.")

        self.animator = self.entity.animator if hasattr(self.entity, 'animator') else None
        self.animations = getattr(settings, 'WEAPON_ANIMATIONS', {
            'idle': 'idle', 'shoot': 'shoot', 'reload': 'reload', 'walk': 'walk', 'aim': 'aim'
        })
        if self.animator:
            try:
                self.animator.play(self.animations['idle'])
            except:
                pass

    def _create_fallback(self, parent, position):
        self.entity = Entity(
            parent=parent,
            model='cube',
            color=color.lime,
            position=position,
            scale=(0.2, 0.1, 0.4),
            collider=None
        )

    def _find_barrel_tip(self, entity):
        if not entity:
            return None
        if entity.name and any(key in entity.name.lower() for key in ['barrel', 'muzzle', 'tip']):
            return entity
        if hasattr(entity, 'children'):
            for child in entity.children:
                result = self._find_barrel_tip(child)
                if result:
                    return result
        return None

    def play_animation(self, name, loop=False):
        if self.animator:
            anim_name = self.animations.get(name, name)
            try:
                self.animator.play(anim_name, loop=loop)
            except:
                pass

    def set_position(self, pos):
        self.entity.position = pos

    def get_world_barrel_pos(self):
        if self.barrel_tip:
            return self.barrel_tip.world_position
        else:
            return self.entity.position + self.entity.forward * 0.8

    def aim(self, aiming, aim_offset=Vec3(0, 0.05, -0.1)):
        if aiming:
            self.entity.position = self.position + aim_offset
        else:
            self.entity.position = self.position

def create_player():
    player = FirstPersonController()
    player.position = (0, 1, 0)
    base_speed = 10
    player_health = PLAYER_MAX_HEALTH

    # Создаём список оружий
    weapons = []
    # 1) Револьвер
    revolver_model = getattr(settings, 'REVOLVER_MODEL', 'models/revolver.glb')
    revolver_scale = getattr(settings, 'REVOLVER_SCALE', 0.5)
    gun1 = Weapon3D(parent=camera, model_path=revolver_model, position=(0.3, -0.2, 0.5), scale=revolver_scale)
    weapons.append(gun1)

    # 2) Второе оружие (автомат)
    rifle_model = getattr(settings, 'SECONDARY_WEAPON_MODEL', 'models/rifle.glb')
    rifle_scale = getattr(settings, 'SECONDARY_WEAPON_SCALE', 0.5)
    gun2 = Weapon3D(parent=camera, model_path=rifle_model, position=(0.3, -0.2, 0.5), scale=rifle_scale)
    gun2.entity.visible = False   # скрываем по умолчанию
    weapons.append(gun2)

    # Активный индекс
    active_weapon_index = 0
    weapons[active_weapon_index].entity.visible = True

    return player, weapons, active_weapon_index, base_speed, player_health