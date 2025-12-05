import pygame
import numpy as np

# --- 1. CONFIGURATION STATIQUE ---
INIT_TILE_SIZE = 16.0
GRID_WIDTH = 100
GRID_HEIGHT = 80

TOOLBAR_HEIGHT = 60
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

# --- Brush Sizes ---
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

world_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
