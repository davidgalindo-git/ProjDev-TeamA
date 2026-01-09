import pygame
from config import *

MINIMAP_SIZE = 180
MINIMAP_POS = (DEFAULT_WINDOW_WIDTH - MINIMAP_SIZE - 20, 20)


def draw_minimap(screen, world, colors):
    # Contour noir
    pygame.draw.rect(screen, (0, 0, 0), (MINIMAP_POS[0] - 3, MINIMAP_POS[1] - 3, MINIMAP_SIZE + 6, MINIMAP_SIZE + 6))

    # Contenu
    mini_surf = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            # Parcourt chaque cellule du monde (world.grid) et
            # dessine un point de la couleur correspondante
            color = colors.get(world.grid[r][c], (0, 0, 0))
            mini_surf.set_at((c, r), color)

    # Agrandissement à la taille de la minimap
    scaled = pygame.transform.scale(mini_surf, (MINIMAP_SIZE, MINIMAP_SIZE))
    screen.blit(scaled, MINIMAP_POS)

    # Cadre Rouge
    vw = (screen.get_width() / (GRID_WIDTH * world.tile_size)) * MINIMAP_SIZE
    vh = ((screen.get_height() - TOOLBAR_HEIGHT) / (GRID_HEIGHT * world.tile_size)) * MINIMAP_SIZE
    vx = (world.camera_x / (GRID_WIDTH * world.tile_size)) * MINIMAP_SIZE
    vy = (world.camera_y / (GRID_HEIGHT * world.tile_size)) * MINIMAP_SIZE

    pygame.draw.rect(screen, (255, 0, 0),
                     (MINIMAP_POS[0] + vx, MINIMAP_POS[1] + vy, min(vw, MINIMAP_SIZE), min(vh, MINIMAP_SIZE)), 2)


def is_minimap_clicked(mouse_pos):
    # Détection de collision (mouse et minimap)
    mx, my = mouse_pos
    return (MINIMAP_POS[0] <= mx <= MINIMAP_POS[0] + MINIMAP_SIZE and
            MINIMAP_POS[1] <= my <= MINIMAP_POS[1] + MINIMAP_SIZE)


def update_camera_from_minimap(mouse_pos, world, screen_w, screen_h):
    mx, my = mouse_pos
    # On contraint mx et my à rester dans les limites de la minimap pour le drag
    mx = max(MINIMAP_POS[0], min(mx, MINIMAP_POS[0] + MINIMAP_SIZE))
    my = max(MINIMAP_POS[1], min(my, MINIMAP_POS[1] + MINIMAP_SIZE))

    # Coordonnées relatives (proportion dans la minimap)
    rel_x = (mx - MINIMAP_POS[0]) / MINIMAP_SIZE
    rel_y = (my - MINIMAP_POS[1]) / MINIMAP_SIZE

    # Repositionnement avec les dimensions ddu monde
    # Grid : Nb de tuiles; Tile_size: Taille par tuile en pixels
    # (Soustraire la moitié de la taille de l'écran pour cadrer au centre)
    world.camera_x = rel_x * (GRID_WIDTH * world.tile_size) - (screen_w / 2)
    world.camera_y = rel_y * (GRID_HEIGHT * world.tile_size) - ((screen_h - TOOLBAR_HEIGHT) / 2)