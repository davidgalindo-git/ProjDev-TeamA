# Caméra, taille des tuiles, grid et logique de dessin

import numpy as np
from config_cg import *

class WorldState:
    def __init__(self):
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int).tolist()
        self.tile_size = INIT_TILE_SIZE
        self.camera_x = 0
        self.camera_y = 0
        self.current_brush = 1
        self.current_terrain = 0

    def paint(self, row, col):
        N = self.current_brush
        offset = -(N // 2)
        for dr in range(offset, offset + N):
            for dc in range(offset, offset + N):
                r = row + dr
                c = col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    self.grid[r][c] = self.current_terrain
