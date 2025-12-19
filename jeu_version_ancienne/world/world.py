import random
import math
import numpy as np
from opensimplex import OpenSimplex
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

