import pygame
from config import *

COULEURS = {
    0: (0, 0, 200),  # Eau
    1: (0, 150, 0),  # Herbe
    2: (150, 75, 0),  # Montagne
    3: (240, 230, 140),  # Sable
    4: (120, 120, 120),  # Pierre
    5: (100, 100, 100),  # S_rock1 (8x8)
    6: (80, 80, 80),  # B_rock (32x32)
    -1: (200, 50, 50)
}


def draw_world(screen, world, asset_manager):
    frame_index = int(pygame.time.get_ticks() / 300) % 3
    # Culling : on ne dessine que ce qui est sur l'écran
    start_c = max(0, int(world.camera_x // world.tile_size))
    start_r = max(0, int(world.camera_y // world.tile_size))
    end_c = min(GRID_WIDTH, start_c + int(screen.get_width() // world.tile_size) + 2)
    end_r = min(GRID_HEIGHT, start_r + int(screen.get_height() // world.tile_size) + 2)

    for r in range(start_r, end_r):
        for c in range(start_c, end_c):
            tid = world.grid[r][c]

            x = c * world.tile_size - world.camera_x
            y = r * world.tile_size - world.camera_y

            # --- LE CHANGEMENT EST ICI ---
            # 1. On récupère l'image correspondante au terrain (tid) et à la taille du zoom
            img = asset_manager.get_texture(tid, world.tile_size, frame_index)

            if img:
                # 2. On "colle" l'image sur l'écran au lieu de dessiner un rect
                screen.blit(img, (x, y))