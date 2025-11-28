import pygame
from settings import GRID_WIDTH, GRID_HEIGHT
from world.state import (
    world_grid,
    TILE_SIZE,
    camera_x,
    camera_y,
)
from assets.terrain_images import terrain_images


def update_terrain_images(raw_images, tile_size):
    """
    Re-scale terrain images based on tile size.
    """
    scaled = {}

    for key, img in raw_images.items():
        scaled[key] = pygame.transform.scale(
            img, (int(tile_size), int(tile_size))
        )

    return scaled


def draw_world(screen,terrain_images):
    """
    Draw the full world grid based on camera position and tile size.
    """
    ts = int(TILE_SIZE)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile = world_grid[y][x]


            img = terrain_images.get(tile)

            if img:
                screen.blit(img, (x * ts + camera_x, y * ts + camera_y))
