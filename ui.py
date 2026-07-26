# ui.py
from ursina import *

def create_ui(player_health):
    health_text = Text(text=f'Health: {player_health}', position=(-0.85, 0.35), scale=2)
    message_text = Text(text='', position=(0, 0.2), origin=(0,0), scale=3, color=color.red)
    return health_text, message_text