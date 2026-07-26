import pygame
import sys
import subprocess
from game_2d import play_2d

# Инициализация Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Главное меню")
clock = pygame.time.Clock()

# Глобальные настройки (цвет и форма для 2D)
player_color = (0, 255, 0)   # зелёный
player_shape = 'circle'      # круг

# Цвета для палитры
COLORS = [
    (255, 0, 0),   # красный
    (0, 255, 0),   # зелёный
    (0, 0, 255),   # синий
    (255, 255, 0), # жёлтый
    (255, 0, 255), # пурпурный
    (0, 255, 255)  # голубой
]

# Функция рисования кнопки
def draw_button(text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect)
        if click[0] == 1 and action:
            action()
    else:
        pygame.draw.rect(screen, color, rect)
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, (255, 255, 255))
    screen.blit(text_surf, (x + (w - text_surf.get_width())//2, y + (h - text_surf.get_height())//2))
    return rect

# Действия для кнопок
def start_game_2d():
    # Запускаем 2D-игру с текущими настройками
    play_2d(player_color, player_shape)
    # После завершения игры (возврата) меню продолжит работу

def start_game_3d():
    pygame.quit()  # закрываем окно меню
    subprocess.Popen(['py', '-3.12', 'game_3d.py'])
    sys.exit()     # завершаем текущий процесс (меню закрыто)

def open_settings():
    settings_menu()

def quit_game():
    pygame.quit()
    sys.exit()

# Меню настроек
def settings_menu():
    global player_color, player_shape
    color_rect_size = 40
    color_start_x = 200
    color_start_y = 200
    shapes = ['circle', 'square', 'triangle']
    running = True
    while running:
        screen.fill((50, 50, 50))
        font = pygame.font.Font(None, 40)
        title = font.render("Настройки", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                # Выбор цвета
                for i, col in enumerate(COLORS):
                    x = color_start_x + i * (color_rect_size + 10)
                    y = color_start_y
                    rect = pygame.Rect(x, y, color_rect_size, color_rect_size)
                    if rect.collidepoint(mx, my):
                        player_color = col
                # Выбор формы
                for i, shape in enumerate(shapes):
                    x = color_start_x + i * 100
                    y = color_start_y + 100
                    rect = pygame.Rect(x, y, 60, 60)
                    if rect.collidepoint(mx, my):
                        player_shape = shape
                # Кнопка "Назад"
                back_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT-80, 120, 40)
                if back_rect.collidepoint(mx, my):
                    running = False

        # Рисуем палитру
        for i, col in enumerate(COLORS):
            x = color_start_x + i * (color_rect_size + 10)
            y = color_start_y
            pygame.draw.rect(screen, col, (x, y, color_rect_size, color_rect_size))
            if col == player_color:
                pygame.draw.rect(screen, (255, 255, 255), (x-2, y-2, color_rect_size+4, color_rect_size+4), 2)

        # Рисуем варианты форм
        for i, shape in enumerate(shapes):
            x = color_start_x + i * 100
            y = color_start_y + 100
            rect = pygame.Rect(x, y, 60, 60)
            if shape == player_shape:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            else:
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            center = (x + 30, y + 30)
            if shape == 'circle':
                pygame.draw.circle(screen, player_color, center, 20)
            elif shape == 'square':
                pygame.draw.rect(screen, player_color, (x+10, y+10, 40, 40))
            elif shape == 'triangle':
                points = [(x+30, y+10), (x+10, y+50), (x+50, y+50)]
                pygame.draw.polygon(screen, player_color, points)

        # Кнопка "Назад"
        pygame.draw.rect(screen, (200, 200, 200), (WIDTH//2 - 60, HEIGHT-80, 120, 40))
        font = pygame.font.Font(None, 30)
        back_text = font.render("Назад", True, (0, 0, 0))
        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT-70))

        pygame.display.flip()
        clock.tick(60)

# Главное меню
def main_menu():
    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Заголовок
        font = pygame.font.Font(None, 60)
        title = font.render("Мой шутер", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        # Кнопки
        draw_button("2D режим", 250, 150, 200, 50, (0, 128, 0), (0, 255, 0), start_game_2d)
        draw_button("3D режим", 350, 150, 200, 50, (0, 0, 128), (0, 0, 255), start_game_3d)
        draw_button("Настройки", 300, 250, 200, 50, (128, 128, 0), (255, 255, 0), open_settings)
        draw_button("Выход", 300, 350, 200, 50, (128, 0, 0), (255, 0, 0), quit_game)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    start_game_3d()   # запускаем 3D сразу