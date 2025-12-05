# Dessin du monde

import pygame

from jeu.main_Mouldi import *

def draw_world(screen, world, assets):
    tile = world.tile_size
    camx, camy = world.camera_x, world.camera_y

    screen_w, screen_h = screen.get_size()
    grid_h = screen_h - TOOLBAR_HEIGHT

    start_col = int(camx // tile)
    start_row = int(camy // tile)
    end_col = min(GRID_WIDTH, int((camx + screen_w) // tile + 1))
    end_row = min(GRID_HEIGHT, int((camy + grid_h) // tile + 1))

    for r in range(start_row, end_row):
        for c in range(start_col, end_col):
            img = assets.get(world.grid[r][c])
            if img:
                screen.blit(img, (c*tile - camx, r*tile - camy))
