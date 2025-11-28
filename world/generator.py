import random, math
try:
    from opensimplex import OpenSimplex
    has_noise = True
except Exception:
    has_noise = False

from settings import (
    GRID_WIDTH, GRID_HEIGHT, INIT_TILE_SIZE,
    TERRAIN_GRASS, TERRAIN_DIRT, TERRAIN_WATER, TERRAIN_SAND
)

from world.state import world_grid, camera_x, camera_y, TILE_SIZE


def generate_random_world():
    """Generate heightmap-based island world. If opensimplex missing, do simple random blobs."""
    global world_grid, camera_x, camera_y, TILE_SIZE

    GRID_W, GRID_H = GRID_WIDTH, GRID_HEIGHT

    # === SIMPLEX NOISE WORLD ===
    if has_noise:
        seed = random.randint(0, 1000000)
        simplex = OpenSimplex(seed=seed)
        scale = random.uniform(8.0, 18.0)
        cx = GRID_W / 2.0
        cy = GRID_H / 2.0
        max_r = random.uniform(GRID_W / 3.0, GRID_W / 2.0)

        # heightmap
        height = [[0.0] * GRID_W for _ in range(GRID_H)]

        for r in range(GRID_H):
            for c in range(GRID_W):
                n = simplex.noise2(c / scale, r / scale)
                n = (n + 1.0) / 2.0
                dist = math.hypot(c - cx, r - cy)
                fall = max(0.0, 1.0 - (dist / max_r) ** 2)
                height[r][c] = n * fall

        land_th = random.uniform(0.28, 0.40)
        mount_th = random.uniform(0.65, 0.85)

        grid = [[0] * GRID_W for _ in range(GRID_H)]

        # assign terrain by height
        for r in range(GRID_H):
            for c in range(GRID_W):
                h = height[r][c]
                if h > mount_th:
                    grid[r][c] = TERRAIN_DIRT
                elif h > land_th:
                    grid[r][c] = TERRAIN_GRASS
                else:
                    grid[r][c] = TERRAIN_WATER

        # beaches
        final = [row[:] for row in grid]
        for r in range(GRID_H):
            for c in range(GRID_W):
                if grid[r][c] in (TERRAIN_GRASS, TERRAIN_DIRT):
                    coastal = False
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr = r + dr
                            cc = c + dc
                            if (
                                0 <= rr < GRID_H
                                and 0 <= cc < GRID_W
                                and grid[rr][cc] == TERRAIN_WATER
                            ):
                                coastal = True
                                break
                        if coastal:
                            break
                    if coastal:
                        final[r][c] = TERRAIN_SAND

        # finalize world grid
        for r in range(GRID_H):
            for c in range(GRID_W):
                world_grid[r][c] = final[r][c]

    # === SIMPLE RANDOM WORLD ===
    else:
        for r in range(GRID_H):
            for c in range(GRID_W):
                rnum = random.random()
                if rnum < 0.35:
                    world_grid[r][c] = TERRAIN_WATER
                elif rnum < 0.7:
                    world_grid[r][c] = TERRAIN_GRASS
                elif rnum < 0.85:
                    world_grid[r][c] = TERRAIN_DIRT
                else:
                    world_grid[r][c] = TERRAIN_SAND

    # reset camera + zoom
    TILE_SIZE = INIT_TILE_SIZE
    camera_x = 0.0
    camera_y = 0.0
