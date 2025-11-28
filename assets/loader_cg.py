import os
import pygame
from config_cg import *

def load_raw_assets():
    assets = {}

    for file in os.listdir(TERRAIN_DIR):
        name, ext = os.path.splitext(file)

        if ext.lower() in IMAGE_EXTENSIONS:
            path = os.path.join(TERRAIN_DIR, file)
            assets[name] = pygame.image.load(path)

    return assets


def scale_assets(raw_assets, tile_size):
    scaled = {}

    for name, img in raw_assets.items():
        scaled[name] = pygame.transform.scale(img, (tile_size, tile_size))

    return scaled
