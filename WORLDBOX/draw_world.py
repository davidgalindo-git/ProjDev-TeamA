import pygame
from config import *
import time

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
    import time
    frame_index = int(time.time() * 3) % 3

    start_c = max(0, int(world.camera_x // world.tile_size))
    start_r = max(0, int(world.camera_y // world.tile_size))
    #culling => évite de calculer ce qui est en dehors de l'écran
    end_c = min(GRID_WIDTH, start_c + int(screen.get_width() // world.tile_size) + 2)
    end_r = min(GRID_HEIGHT, start_r + int(screen.get_height() // world.tile_size) + 2)

    # 1. Dessiner le SOL
    for r in range(start_r, end_r):
        for c in range(start_c, end_c):
            tid = world.grid[r][c]
            x = c * world.tile_size - world.camera_x
            y = r * world.tile_size - world.camera_y
            size = int(world.tile_size) + 1

            # Si c'est un rocher(4) ou arbre(5), on met de l'herbe(1) dessous
            sol_id = 1 if tid in [4, 5] else tid
            img = asset_manager.get_texture(sol_id, size, frame_index)
            if img: screen.blit(img, (x, y))

    # 2. Dessiner les OBJETS
    for r in range(start_r, end_r):
        for c in range(start_c, end_c):
            tid = world.grid[r][c]
            if tid not in [4, 5]: continue
            #une fois le  sol dessiné, il passera a l objet

            x = c * world.tile_size - world.camera_x
            y = r * world.tile_size - world.camera_y
            size = int(world.tile_size) + 1

            img = asset_manager.get_texture(tid, size, frame_index)
            if img:
                if tid == 5: # Arbre
                    # éviter le décalage de l'arbre
                    dx = x - (img.get_width() - size) // 2
                    dy = y - (img.get_height() - size)
                    screen.blit(img, (dx, dy))
                else: # Rocher
                    screen.blit(img, (x, y))