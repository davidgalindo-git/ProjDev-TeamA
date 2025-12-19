import pygame
import random
import opensimplex as OpenSimplex
import numpy as np
import math
import jeu.globals as G

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

def generate_random_world():
    """Génère un monde aléatoire avec Simplex Noise pour des formes naturelles et biomes mélangés."""

    # Réinitialisation de la caméra et du zoom
    G.TILE_SIZE = G.INIT_TILE_SIZE
    G.camera_x = 0.0
    G.camera_y = 0.0

    # Paramètres de bruit aléatoires pour la HAUTEUR et la forme de l'île
    seed_height = random.randint(0, 100000)
    simplex_height = OpenSimplex(seed=seed_height)

    # Scale très aléatoire pour garantir des formes d'îles très différentes
    SCALE_HEIGHT = random.uniform(8.0, 20.0)
    OFFSET_X = random.uniform(0.0, 1000.0)
    OFFSET_Y = random.uniform(0.0, 1000.0)

    CENTER_X = G.GRID_WIDTH / 2.0
    CENTER_Y = G.GRID_HEIGHT / 2.0

    # Le rayon peut être plus grand ou plus petit pour créer des continents ou des archipels
    MAX_RADIUS = random.uniform(G.GRID_WIDTH / 3.0, G.GRID_WIDTH / 2.0)

    # Seuils aléatoires pour plus de variété
    MOUNTAIN_THRESHOLD = random.uniform(0.65, 0.85)
    LAND_THRESHOLD = random.uniform(0.3, 0.4)

    # 1. GÉNÉRATION DE LA CARTE DE HAUTEUR
    height_map = np.zeros((G.GRID_HEIGHT, G.GRID_WIDTH), dtype=float)

    for r in range(G.GRID_HEIGHT):
        for c in range(G.GRID_WIDTH):
            # 1a. Bruit de Hauteur (Détermine si c'est de l'eau, terre ou montagne)
            noise_val_h = simplex_height.noise2(x=(c + OFFSET_X) / SCALE_HEIGHT, y=(r + OFFSET_Y) / SCALE_HEIGHT)
            normalized_noise_h = (noise_val_h + 1.0) / 2.0

            # Déformation du centre : force les bords à être de l'eau
            dist_to_center = math.sqrt((c - CENTER_X) ** 2 + (r - CENTER_Y) ** 2)
            edge_falloff = 1.0 - (dist_to_center / MAX_RADIUS) ** 2

            final_height = normalized_noise_h * max(0, edge_falloff)
            height_map[r, c] = final_height

    # 2. APPLICATION DES SEUILS ET CRÉATION DE LA GRILLE
    new_grid = np.zeros((G.GRID_HEIGHT, G.GRID_WIDTH), dtype=int)

    # Remplissage par défaut : Herbe (Type 1) pour les terres moyennes
    new_grid[(height_map > LAND_THRESHOLD)] = 1

    # Application de la Montagne/Terre Rugueuse (Type 2) sur les hauteurs
    new_grid[(height_map > MOUNTAIN_THRESHOLD)] = 2

    # Le reste est de l'eau (Type 0 par défaut de new_grid)

    # 3. POST-PROCESSUS: CRÉATION DES PLAGES DE SABLE
    final_grid = new_grid.copy()

    for r in range(G.GRID_HEIGHT):
        for c in range(G.GRID_WIDTH):
            if final_grid[r, c] == 1 or final_grid[r, c] == 2:  # Si c'est Herbe ou Montagne/Terre
                is_coastal = False

                # Vérifier si un voisin (y compris les diagonales) est de l'eau (0)
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0: continue

                        nr, nc = r + dr, c + dc

                        if 0 <= nr < G.GRID_HEIGHT and 0 <= nc < G.GRID_WIDTH:
                            if new_grid[nr, nc] == 0:
                                is_coastal = True
                                break
                    if is_coastal: break

                # Règle : Les tuiles Herbe ou Montagne adjacentes à l'eau deviennent du sable (3).
                if is_coastal:
                    final_grid[r, c] = 3

    G.world_grid = final_grid.tolist()