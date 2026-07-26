from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Цвет фона – голубое небо
window.color = color.rgb(135, 206, 235)

# Зелёный пол (плоскость)
ground = Entity(
    model='plane',
    scale=(100, 1, 100),
    color=color.rgb(50, 180, 50),
    position=(0, -0.5, 0),
    collider='box'
)

# Игрок
player = FirstPersonController()
player.position = (0, 1, 0)

app.run()