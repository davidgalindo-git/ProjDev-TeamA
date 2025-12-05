# Fichier : rendering/draw_element_cg.py

import pygame


def get_element_images(assets, TILE_SIZE, ELEMENT_SCALE_FACTOR):
    """Prépare les images des éléments à la bonne taille, proportionnellement au zoom du terrain."""
    element_images = {}
    rock_id = 5
    raw_img = assets.get(rock_id)

    if raw_img:
        # L'image est redimensionnée à la taille de la TILE_SIZE actuelle (e.g. 16, 32, 64...)
        new_size = int(TILE_SIZE)

        scaled_img = pygame.transform.scale(raw_img, (new_size, new_size))
        element_images[rock_id] = scaled_img.convert_alpha()

        # Création de la version semi-transparente (pour l'aperçu)
        ghost_img = scaled_img.copy()
        ghost_img.set_alpha(100)
        element_images['GHOST'] = ghost_img

    return element_images


def draw_elements(screen, WorldData, element_grid, TERRAIN_IMAGES_RAW, is_drawing, element_type):
    # Nouvelle taille de l'élément (basée sur le zoom actuel)
    # L'élément 8x8 est dessiné sur un carré de TILE_SIZE.
    # On va le dessiner dans le bloc 16x16, donc la taille doit être TILE_SIZE (16x16)
    current_element_size = int(WorldData.tile_size)

    # 1. Redimensionner l'image RAW du rocher (Type 5)
    # On redimensionne l'image brute 16x16 (du rock) à la taille actuelle de la tuile.
    image_to_draw_raw = TERRAIN_IMAGES_RAW.get(element_type)

    # IMPORTANT : Utiliser pygame.transform.scale pour s'adapter au TILE_SIZE actuel
    if image_to_draw_raw:
        # Redimensionner l'image pour qu'elle corresponde à la taille de la tuile 16x16
        # Si TILE_SIZE est 32, l'image sera 32x32.
        image_to_draw = pygame.transform.scale(
            image_to_draw_raw, (current_element_size, current_element_size)
        ).convert_alpha()
    else:
        return  # Rien à dessiner

    # Déterminer la zone de dessin visible (en indices de la grille 8x8)
    # La grille 8x8 a un pas de WorldData.ELEMENT_GRID_SIZE (qui est 8)
    # La taille de chaque "cellule" affichée est WorldData.tile_size

    screen_width, screen_height = screen.get_size()

    # Calcul des indices de la grille 8x8 visibles, en utilisant le pas de la caméra (element_grid_size)
    # et la taille d'affichage réelle (tile_size)

    # Le pas de la grille d'éléments (en pixels monde) est element_grid_size * (tile_size/INIT_TILE_SIZE)
    # Mais le plus simple est de se baser sur la grille 16x16 visible et de la doubler

    # On utilise la grille 16x16 pour calculer la zone visible (plus robuste)
    start_col_16 = max(0, int(WorldData.camera_x // WorldData.tile_size))
    end_col_16 = min(WorldData.GRID_WIDTH, int((WorldData.camera_x + screen_width) // WorldData.tile_size + 1))
    start_row_16 = max(0, int(WorldData.camera_y // WorldData.tile_size))
    end_row_16 = min(WorldData.GRID_HEIGHT,
                     int((WorldData.camera_y + screen_height - WorldData.TOOLBAR_HEIGHT) // WorldData.tile_size + 1))

    # La grille 8x8 est deux fois plus grande (ELEMENT_SCALE_FACTOR = 2)
    start_col_el = start_col_16 * 2
    end_col_el = end_col_16 * 2
    start_row_el = start_row_16 * 2
    end_row_el = end_row_16 * 2

    # Parcourir la grille 8x8 (element_grid) dans la zone visible
    for r in range(start_row_el, end_row_el):
        for c in range(start_col_el, end_col_el):

            if 0 <= r < len(element_grid) and 0 <= c < len(element_grid[0]):

                element_val = element_grid[r][c]

                if element_val == element_type:
                    # Position mondiale de la cellule 8x8
                    # c * 8 donne la position dans un monde 1x1 = 8 pixels
                    # Si TILE_SIZE = 16 (zoom normal), chaque cellule 8x8 occupe 8 pixels.
                    # Pour utiliser le zoom (TILE_SIZE), on doit ajuster la position.

                    # Position X, Y de la tuile 16x16 qui contient ce bloc 8x8
                    # (c // 2) * WorldData.tile_size

                    # Mais on utilise l'image redimensionnée (taille TILE_SIZE) pour recouvrir le carré 16x16.
                    # Si on place le rocher sur le coin de la tuile 16x16, on voit le rocher sur la tuile du bas ou de droite

                    # Position en pixels dans le monde, basée sur la taille initiale de l'élément (8)
                    world_x = c * WorldData.ELEMENT_GRID_SIZE
                    world_y = r * WorldData.ELEMENT_GRID_SIZE

                    # On applique l'échelle du zoom.
                    # L'échelle du zoom est TILE_SIZE / INIT_TILE_SIZE (ex: 32/16 = 2)
                    scale = WorldData.tile_size / WorldData.INIT_TILE_SIZE

                    # Nouvelle position monde mise à l'échelle
                    scaled_world_x = world_x * scale
                    scaled_world_y = world_y * scale

                    # Position à l'écran (moins la caméra)
                    screen_x = scaled_world_x - WorldData.camera_x
                    screen_y = scaled_world_y - WorldData.camera_y

                    # Dessiner l'image redimensionnée (qui a la taille TILE_SIZE)
                    # Note: L'image du rocher doit techniquement couvrir 2x2 blocs 8x8 (donc un bloc 16x16)
                    # Si l'image 'S_rock1.png' est de 16x16 pixels, on la dessine sur l'espace 16x16.

                    # Dessiner le rocher (qui est déjà mis à l'échelle à TILE_SIZE x TILE_SIZE)
                    screen.blit(image_to_draw, (screen_x, screen_y))

                    # DEBUG (Optionnel: pour voir les bornes des rochers)
                    # if screen_x < screen_width and screen_y < screen_height - WorldData.TOOLBAR_HEIGHT:
                    #     pygame.draw.rect(screen, (255, 0, 255), (screen_x, screen_y, current_element_size, current_element_size), 1)