# Charger les textures et échelles

import pygame
from config_cg import *

def load_raw_assets():
    return {
        0: pygame.image.load("assets/water.png").convert_alpha(),
        1: pygame.image.load("assets/grass.png").convert_alpha(),
        2: pygame.image.load("assets/dirt.png").convert_alpha(),
        3: pygame.image.load("assets/sand.png").convert_alpha(),
        4: pygame.image.load("assets/stone.png").convert_alpha(),
    }

def scale_assets(assets, tile_size):
    new = {}
    for k, img in assets.items():
        new[k] = pygame.transform.scale(img, (int(tile_size), int(tile_size)))
    return new
