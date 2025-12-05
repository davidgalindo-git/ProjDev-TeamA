import pygame
import numpy as np

pygame.init()

TOOLBAR_HEIGHT = 60
INIT_TILE_SIZE = 16.0

# --- ÉTATS DE L'APPLICATION ---
APP_STATE = "START_SCREEN"

# Variables de l'état du jeu
TILE_SIZE = INIT_TILE_SIZE
camera_x = 0.0
camera_y = 0.0
is_panning = False
last_mouse_pos = (0, 0)
minimap_dragging = False
minimap_drag_offset = (0, 0)

# Variables de défilement de l'ui
scroll_offset = 0
BUTTON_GAP = 10
BUTTON_BASE_WIDTH = 50
BUTTON_HEIGHT = TOOLBAR_HEIGHT - BUTTON_GAP

# Fonts
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 48)
label_font = pygame.font.SysFont("comicsans", 15)

# --- 1. CONFIGURATION STATIQUE ---
GRID_WIDTH = 100
GRID_HEIGHT = 80

SCROLL_BUTTON_WIDTH = 50

# Dimensions de la fenêtre par défaut
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700

# Couleurs pour les types de terrain (MAINTENU UNIQUEMENT POUR L'AFFICHAGE DE L'ui)
COLORS = {
    0: (0, 0, 200),  # Eau
    1: (0, 150, 0),  # Herbe
    2: (150, 75, 0),  # Montagne
    3: (240, 230, 140),  # Sable
    4: (120, 120, 120)  # Pierre
}

clock = pygame.time.Clock()
# --- Toolbar ---
TOOLBAR_BUTTONS = [
    {"type": 0, "label": "Water"},
    {"type": 1, "label": "Grass"},
    {"type": 2, "label": "Dirt"},
    {"type": 3, "label": "Sand"},
    {"type": 4, "label": "Stone"},
    {"type": "BRUSH_1", "label": "x1", "brush": 1},
    {"type": "BRUSH_2", "label": "x2", "brush": 2},
    {"type": "BRUSH_3", "label": "x4", "brush": 4},
    {"type": "BRUSH_4", "label": "x8", "brush": 8},
    {"type": "BRUSH_5", "label": "x16", "brush": 16},
    {"type": "BRUSH_6", "label": "x32", "brush": 32}
]
CURRENT_TERRAIN = TOOLBAR_BUTTONS[0]["type"]

BUTTON_GAP = 10
BUTTON_BASE_WIDTH = 50
BUTTON_HEIGHT = TOOLBAR_HEIGHT - BUTTON_GAP

BRUSH_SIZES = [1, 4, 16, 64]
CURRENT_BRUSH = 1  # default 1x1

TERRAIN_IMAGES_RAW = {}
TERRAIN_IMAGES = {}

# --- World Time Simulation ---
timer_active = False
MAX_DAYS = 1000
world_minutes = 0
world_hours = 0
world_days = 0
display_hours = 0
# 1 real second = 1 game hour
GAME_HOURS_PER_SECOND = 1
# buttons
timer_button = pygame.Rect(20, 20, 120, 40)
# Time bar
TIME_BAR_RECT = pygame.Rect(150, 60, 400, 20)  # x, y, width, height
# Day bar
DAY_BAR_RECT = pygame.Rect(150, 20, 400, 20)  # x, y, width, height

# --- World Creation ---
world_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)