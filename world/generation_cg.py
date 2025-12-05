# Fichier : generation_cg.py

import random, math
import numpy as np
from opensimplex import OpenSimplex
# Import de la configuration
from config_cg import GRID_WIDTH, GRID_HEIGHT

def generate_random_world():
    """Génère un monde aléatoire avec Simplex Noise."""

    # Utilisation de constantes locales ou de la configuration pour la génération
    seed_height = random.randint(0, 100000)
    simplex_height = OpenSimplex(seed=seed_height)

    SCALE_HEIGHT = random.uniform(8.0, 20.0)
    OFFSET_X = random.uniform(0.0, 1000.0)
    OFFSET_Y = random.uniform(0.0, 1000.0)

    CENTER_X = GRID_WIDTH / 2.0
    CENTER_Y = GRID_HEIGHT / 2.0
    MAX_RADIUS = random.uniform(GRID_WIDTH / 3.0, GRID_WIDTH / 2.0)
    MOUNTAIN_THRESHOLD = random.uniform(0.65, 0.85)
    LAND_THRESHOLD = random.uniform(0.3, 0.4)

    height_map = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=float)

    # ... (Le reste de la logique de calcul de la height_map reste identique) ...
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            noise_val_h = simplex_height.noise2(x=(c + OFFSET_X) / SCALE_HEIGHT, y=(r + OFFSET_Y) / SCALE_HEIGHT)
            normalized_noise_h = (noise_val_h + 1.0) / 2.0

            dist_to_center = math.sqrt((c - CENTER_X) ** 2 + (r - CENTER_Y) ** 2)
            edge_falloff = 1.0 - (dist_to_center / MAX_RADIUS) ** 2

            final_height = normalized_noise_h * max(0, edge_falloff)
            height_map[r, c] = final_height

    # base terrain
    new_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
    new_grid[(height_map > LAND_THRESHOLD)] = 1
    new_grid[(height_map > MOUNTAIN_THRESHOLD)] = 2

    # beaches
    final_grid = new_grid.copy()
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            if final_grid[r, c] in (1, 2):
                is_coastal = False
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                            if new_grid[nr, nc] == 0:
                                is_coastal = True
                                break
                    if is_coastal: break

                if is_coastal:
                    final_grid[r, c] = 3

    return final_grid.tolist()