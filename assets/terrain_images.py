import pygame
from assets.loader_cg import load_raw_assets, scale_assets
from world.state import TILE_SIZE


_raw_assets = load_raw_assets()


terrain_images = scale_assets(_raw_assets, TILE_SIZE)
