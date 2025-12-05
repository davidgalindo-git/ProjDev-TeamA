# Fichier : jeu/imageLoader.py (CORRECTION INTÉGRALE)

import pygame
import sys
# Utilise les imports ABSOLUS directs pour les constantes (comme dans worldManagement)
from config_cg import INIT_TILE_SIZE

ASSETS_PATH = "assets/"


def load_all_assets():
    """Charge toutes les images brutes. Retourne le dictionnaire des images RAW."""
    image_files = {
        0: "water.png", 1: "grass.png", 2: "dirt.png", 3: "sand.png",
        4: "stone.png", 5: "S_rock1.png", 6: "B_rock.png",
    }
    raw_images = {}
    try:
        for terrain_id, filename in image_files.items():
            path = ASSETS_PATH + filename
            raw_images[terrain_id] = pygame.image.load(path).convert_alpha()
        return raw_images
    except pygame.error as e:
        print(f"Erreur de chargement d'image. Vérifiez le dossier '{ASSETS_PATH}'. Erreur: {e}")
        sys.exit()


def update_terrain_images(image_cache: dict, raw_images: dict, current_tile_size: float):
    """
    Redimensionne toutes les textures pour le zoom actuel et met à jour le cache (image_cache).
    """
    if not raw_images:
        return

    # Vérification simplifiée de la taille
    current_size = image_cache.get(0).get_size()[0] if 0 in image_cache else -1

    if current_size != int(current_tile_size):
        new_images = {}
        target_size = int(current_tile_size)

        for terrain_type, raw_img in raw_images.items():
            new_images[terrain_type] = pygame.transform.scale(
                raw_img, (target_size, target_size)
            )
        # Met à jour le cache (TERRAIN_IMAGES)
        image_cache.clear()
        image_cache.update(new_images)