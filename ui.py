# ui.py
from ursina import *

def create_ui(player_health):
    health_text = Text(text=f'Health: {player_health}', position=(-0.85, 0.35), scale=2)
    message_text = Text(text='', position=(0, 0.2), origin=(0,0), scale=3, color=color.red)
    return health_text, message_text

def create_ammo_ui(ammo_clip, ammo_reserve):
    ammo_text = Text(text=f'{ammo_clip} / {ammo_reserve}', position=(0.8, -0.4), scale=2, origin=(0,0), color=color.white)
    return ammo_text

def update_ammo_ui(ammo_text, ammo_clip, ammo_reserve, reloading=False):
    if reloading:
        ammo_text.text = '⟳ Перезарядка...'
    else:
        ammo_text.text = f'{ammo_clip} / {ammo_reserve}'