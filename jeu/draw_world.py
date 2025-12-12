# Fichier: draw_world.py

import pygame


def draw_world(screen, world, image_manager):
    """Dessine le terrain 16x16 visible."""
    tile = world.tile_size
    camx, camy = world.camera_x, world.camera_y

    screen_w, screen_h = screen.get_size()

    # Le world object fournit les indices visibles
    start_row, end_row, start_col, end_col = world.get_visible_tile_range(screen_w, screen_h)

    for r in range(start_row, end_row):
        for c in range(start_col, end_col):
            asset_id = world.grid[r][c]

            # Utilisation de l'ImageManager
            img = image_manager.get_scaled_image(asset_id, tile)

            if img:
                # Positionnement : (indice * taille - caméra offset)
                screen.blit(img, (c * tile - camx, r * tile - camy))


# --- Dessin des Éléments (8x8) ---

def draw_elements(screen, world, image_manager, screen_width, screen_height):
    """Dessine les éléments de la grille 8x8."""

    # La taille d'affichage de l'élément correspond à la taille de la tuile 16x16
    current_element_size = world.tile_size

    start_row_el, end_row_el, start_col_el, end_col_el = \
        world.get_visible_element_range(screen_width, screen_height)

    # Parcourir la grille 8x8
    for r in range(start_row_el, end_row_el):
        for c in range(start_col_el, end_col_el):

            element_val = world.element_grid[r][c]

            # On ne dessine que l'ancrage (valeur > 0)
            if element_val > 0:

                # --- Calcul de la position mondiale mise à l'échelle ---

                # Position en pixels monde basés sur la grille 8x8 (World.ELEMENT_GRID_SIZE = 8)
                world_x = c * world.ELEMENT_GRID_SIZE
                world_y = r * world.ELEMENT_GRID_SIZE

                # Appliquer l'échelle du zoom. Scale = TILE_SIZE / INIT_TILE_SIZE
                scale = world.tile_size / world.INIT_TILE_SIZE

                scaled_world_x = world_x * scale
                scaled_world_y = world_y * scale

                # --- Position à l'écran ---
                screen_x = scaled_world_x - world.camera_x
                screen_y = scaled_world_y - world.camera_y

                # Utilisation de l'ImageManager
                image_to_draw = image_manager.get_scaled_image(element_val, current_element_size)

                if image_to_draw:
                    screen.blit(image_to_draw, (screen_x, screen_y))


# --- Fonction utilitaire pour l'aperçu du pinceau (Ghost) ---

def draw_brush_preview(screen, world, mouse_x, mouse_y, grid_bottom_y):
    """Dessine l'aperçu du pinceau carré sur la grille."""

    if mouse_y >= grid_bottom_y:
        return

    tile_size = world.tile_size
    brush_size = world.current_brush_size

    # Conversion de la position souris en position monde (centre du pinceau)
    world_x_center = mouse_x + world.camera_x
    world_y_center = mouse_y + world.camera_y

    # Conversion en indice de tuile 16x16 pour l'ancrage
    grid_col = int(world_x_center // tile_size)
    grid_row = int(world_y_center // tile_size)

    N = brush_size
    start_offset = -(N // 2)

    # Utilisation d'une image générique pour l'aperçu
    preview_color = (200, 200, 200, 100)  # Remplissage semi-transparent

    for dr in range(start_offset, start_offset + N):
        for dc in range(start_offset, start_offset + N):
            r = grid_row + dr
            c = grid_col + dc

            if 0 <= r < world.GRID_HEIGHT and 0 <= c < world.GRID_WIDTH:
                # Calcul de la position écran pour le carré
                screen_x = c * tile_size - world.camera_x
                screen_y = r * tile_size - world.camera_y

                # Dessin du rectangle semi-transparent (simulant le pinceau)
                preview_rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)

                # Pour les aperçus complexes, utiliser une surface alpha
                s = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                s.fill(preview_color)
                screen.blit(s, (screen_x, screen_y))

                # Bordure
                pygame.draw.rect(screen, (255, 255, 255), preview_rect, 1)

# Le dessin des aperçus d'éléments (Ghost Images) peut être ajouté ici,
# en utilisant image_manager.get_element_ghost_image().