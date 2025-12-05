# Paramètres généraux

# Paramètres généraux
INIT_TILE_SIZE = 16.0
GRID_WIDTH = 100
GRID_HEIGHT = 80

# Paramètres des Éléments (grille 2x plus fine)
ELEMENT_GRID_SIZE_PIXELS = 8  # 8x8 pixels initial
ELEMENT_SCALE_FACTOR = int(INIT_TILE_SIZE / ELEMENT_GRID_SIZE_PIXELS)  # 16 / 8 = 2
ELEMENT_GRID_WIDTH = GRID_WIDTH * ELEMENT_SCALE_FACTOR  # 200
ELEMENT_GRID_HEIGHT = GRID_HEIGHT * ELEMENT_SCALE_FACTOR  # 160

# La taille de la grande pierre en cellules d'éléments (8x8)
BIG_ROCK_SIZE_ELEMENTS = 4  # 4x4 cellules d'éléments = 32x32px initial
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700

TOOLBAR_HEIGHT = 60
SCROLL_BUTTON_WIDTH = 50

COLORS = {
    0: (0, 0, 200),
    1: (0, 150, 0),
    2: (150, 75, 0),
    3: (240, 230, 140),
    4: (120, 120, 120),
}

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
    {"type": "BRUSH_6", "label": "x32", "brush": 32},
]
