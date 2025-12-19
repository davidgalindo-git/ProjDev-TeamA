import pygame

# Dimensions de la grille
GRID_WIDTH = 100
GRID_HEIGHT = 80
INIT_TILE_SIZE = 32

# Dimensions élément (8x8)
ELEMENT_SCALE_FACTOR = 2
ELEMENT_GRID_WIDTH = GRID_WIDTH * ELEMENT_SCALE_FACTOR
ELEMENT_GRID_HEIGHT = GRID_HEIGHT * ELEMENT_SCALE_FACTOR

# Fenêtre
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
TOOLBAR_HEIGHT = 100

#Toolbar
TOOLBAR_HEIGHT = 80
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40

# Timer
timer_active = False
world_hours = 8.0
world_minutes = 0
world_days = 1
MAX_DAYS = 100
GAME_HOURS_PER_SECOND = 1.0

# États de l'UI
day_bar_dragging = False
time_bar_dragging = False

# Rects UI
timer_button = pygame.Rect(20, 20, 120, 40)
TIME_BAR_RECT = pygame.Rect(150, 60, 400, 20)
DAY_BAR_RECT = pygame.Rect(150, 20, 400, 20)