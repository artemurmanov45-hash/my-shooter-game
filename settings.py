ROOM_SIZE = 40
WALL_HEIGHT = 40.0
WALL_THICKNESS = 0.2
DOOR_WIDTH = 8.0
DOOR_HEIGHT = 3.0
WINDOW_WIDTH = 1.5
WINDOW_HEIGHT = 1.5
WINDOW_Y = 1.8
PLAYER_MAX_HEALTH = 100
GRID_SIZE = 3

# ---------- НАСТРОЙКИ ОКНА ----------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# ---------- ТЕКСТУРЫ ----------
TEXTURE_FLOOR = 'textures/floor.jpg'
TEXTURE_CEILING = 'textures/ceiling.jpg'
TEXTURE_WALL_OUTER = 'textures/wall_outer.jpg'
TEXTURE_WALL_INNER = 'textures/wall_inner.jpg'
TEXTURE_ENEMY_BODY = 'textures/enemy_body.png'

# ---------- ТЕКСТУРЫ МЕНЮ ----------
TEXTURE_MENU_BG = 'textures/menu_bg.jpg'
TEXTURE_LOGO = 'textures/logo.png'

# ---------- ЗВУКИ ----------
SOUND_GUNSHOT = 'sounds/gunshot.wav'
SOUND_ENEMY_SHOT = 'sounds/enemy_shot.wav'
SOUND_HIT = 'sounds/hit.wav'
SOUND_MENU_CLICK = 'sounds/menu_click.wav'
SOUND_MENU_MUSIC = 'sounds/menu_music.wav'
SOUND_GAME_MUSIC = 'sounds/game_music.wav'
SOUND_RELOAD = 'sounds/reload.wav'
SOUND_VOICE_RELOAD = 'sounds/voice_reload.wav'   # реплика героя при первой перезарядке

# ---------- ГРОМКОСТЬ ----------
VOLUME_GUNSHOT = 3.0
VOLUME_ENEMY_SHOT = 0.5
VOLUME_HIT = 1.0
VOLUME_MENU_CLICK = 1.0
VOLUME_MENU_MUSIC = 0.6
VOLUME_GAME_MUSIC = 0.4
VOLUME_RELOAD = 2.0
VOLUME_VOICE_RELOAD = 1.5   # громкость голосовой реплики

# ---------- ВРАГИ ----------
ENEMY_WALK_SPEED = 4.0
ENEMY_JUMP_HEIGHT = 0.5
ENEMY_JUMP_INTERVAL = 2.0
ENEMY_MODEL = 'models/monster.glb'

# ---------- СКОРОСТРЕЛЬНОСТЬ ----------
FIRE_RATE = 1

# ---------- ПАРАМЕТРЫ СЕТКИ КОМНАТ ----------
GRID_ROOMS_X = 3
GRID_ROOMS_Z = 3
GRID_ROOM_WIDTH = 25
GRID_ROOM_DEPTH = 25
GRID_WALL_THICKNESS = 0.8
GRID_DOOR_WIDTH = 13.5
GRID_DOOR_HEIGHT = 6.0
GRID_DOOR_PROBABILITY = 1.0

# ---------- ПАРАМЕТРЫ ЭТАЖЕЙ ----------
HOLE_SIZE = 4.0

# ---------- ОРУЖИЕ ----------
REVOLVER_MODEL = 'models/revolver.glb'
REVOLVER_SCALE = 0.5
SECONDARY_WEAPON_MODEL = 'models/rifle.glb'
SECONDARY_WEAPON_SCALE = 0.5

# ---------- КОЛИЧЕСТВО ПИКАПОВ НА ЭТАЖ ----------
PICKUP_COUNT_PER_FLOOR = 4

# ---------- АНИМАЦИИ ОРУЖИЯ ----------
WEAPON_ANIMATIONS = {
    'idle': 'idle',
    'shoot': 'shoot',
    'reload': 'reload',
    'walk': 'walk',
    'aim': 'aim'
}

# ---------- ПАРАМЕТРЫ ЛИФТА ----------
ELEVATOR_SPEED = 4.0
ELEVATOR_POSITION = (0, 0)

# ---------- ТЕКСТУРЫ КАРТИН ----------
PAINTING_FOLDER = 'textures/paintings/'   # путь к файлу с изображением (можно несколько)
PAINTING_MAX_COUNT = 2                    # максимальное количество картин на всю карту (0 - отключить)
PICTURE_HEIGHT = 3.0                         # высота центра картины
PICTURE_SIZE = 2.7                           # размер стороны (квадрат)
PICTURE_SPACING = 3.1                  # расстояние между двумя картинами по горизонтали