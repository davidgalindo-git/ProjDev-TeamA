# Générer le monde aléatoire

import random, math
import numpy as np
from opensimplex import OpenSimplex
from config_cg import *

def generate_random_world():
    seed_height = random.randint(0, 100000)
    simplex_height = OpenSimplex(seed=seed_height)

    SCALE = random.uniform(8, 20)
    OFFSET_X = random.uniform(0, 1000)
    OFFSET_Y = random.uniform(0, 1000)
    CENTER_X = GRID_WIDTH / 2
    CENTER_Y = GRID_HEIGHT / 2
    MAX_RADIUS = random.uniform(GRID_WIDTH/3, GRID_WIDTH/2)

    LAND_TH = random.uniform(0.3, 0.4)
    MNT_TH = random.uniform(0.65, 0.85)

    height_map = np.zeros((GRID_HEIGHT, GRID_WIDTH))

    # height field
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            n = simplex_height.noise2((c + OFFSET_X)/SCALE, (r + OFFSET_Y)/SCALE)
            n = (n + 1) / 2

            dist = math.dist((c, r), (CENTER_X, CENTER_Y))
            falloff = 1 - (dist / MAX_RADIUS)**2
            falloff = max(0, falloff)

            height_map[r, c] = n * falloff

    # base terrain
    grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
    grid[height_map > LAND_TH] = 1
    grid[height_map > MNT_TH] = 2

    # beaches
    final = grid.copy()
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            if final[r,c] in (1,2):
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        if dr==0 and dc==0: continue
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                            if grid[nr,nc] == 0:
                                final[r,c] = 3
                                break
                    else:
                        continue
                    break

    return final.tolist()
