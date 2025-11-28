# world/state.py

from settings import GRID_WIDTH, GRID_HEIGHT

# World data
world_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Camera system
camera_x = 0
camera_y = 0
TILE_SIZE = 32

# Brush & terrain
CURRENT_TERRAIN = 1
CURRENT_BRUSH = 1

# Panning
is_panning = False
pan_start_x = 0
pan_start_y = 0
mouse_start_cam_x = 0
mouse_start_cam_y = 0

# Application states
APP_START = "START"
APP_RUNNING = "RUNNING"

# Current app state
APP_STATE = APP_START


def set_app_state(new_state):
    global APP_STATE
    APP_STATE = new_state

# Unified UI state dictionary (toolbar & UI için)
state = {
    "current_terrain": CURRENT_TERRAIN,
    "current_brush": CURRENT_BRUSH,
    "app_state": APP_STATE,
    "is_panning": is_panning,
    "tile_size": TILE_SIZE,
    "camera_x": camera_x,
    "camera_y": camera_y
}


