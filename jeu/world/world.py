import jeu.globals as G
from jeu.assets.images import update_terrain_images

def draw_world(screen_width, grid_bottom_y):
    """Dessine la grille visible en utilisant les images redimensionnées (INCHANGÉE)."""
    G.TILE_SIZE = max(G.TILE_SIZE, min(G.min_tile_size_x, G.min_tile_size_y))

    # Correction de la position de la Caméra (INCHANGÉ)
    max_camera_x = max(0.0, G.GRID_WIDTH * G.TILE_SIZE - screen_width)
    max_camera_y = max(0.0, G.GRID_HEIGHT * G.TILE_SIZE - grid_bottom_y)

    G.camera_x = max(0.0, min(G.camera_x, max_camera_x))
    G.camera_y = max(0.0, min(G.camera_y, max_camera_y))

    # Redimensionner les images pour la G.TILE_SIZE actuelle
    update_terrain_images()

    # Dessin des tuiles visibles
    start_col = max(0, int(G.camera_x // G.TILE_SIZE))
    end_col = min(G.GRID_WIDTH, int((G.camera_x + screen_width) // G.TILE_SIZE + 1))
    start_row = max(0, int(G.camera_y // G.TILE_SIZE))
    end_row = min(G.GRID_HEIGHT, int((G.camera_y + grid_bottom_y) // G.TILE_SIZE + 1))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            terrain_type = G.world_grid[row][col]

            # Utiliser l'image redimensionnée
            image_to_draw = G.TERRAIN_IMAGES.get(terrain_type)

            if image_to_draw:
                screen_x = col * G.TILE_SIZE - G.camera_x
                screen_y = row * G.TILE_SIZE - G.camera_y

                # Dessin de l'image (texture)
                G.screen.blit(image_to_draw, (screen_x, screen_y))

