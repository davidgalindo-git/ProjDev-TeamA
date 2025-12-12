# Fichier: images.py

import pygame


# Supposons que ces constantes sont importées (ou définies)
# INIT_TILE_SIZE = 16

class ImageManager:
    """Gère le chargement, le stockage et la mise à l'échelle des assets."""

    def __init__(self):
        self.raw_assets = {}  # Assets bruts chargés (non mis à l'échelle)
        self.scaled_cache = {}  # Cache des images mises à l'échelle {tile_size: {id: image}}
        # Définir ici les IDs d'assets (ex: 0=Water, 1=Grass, 5=Rock, etc.)
        self.ASSET_PATHS = {
            1: "assets/img/grass.png",
            5: "assets/img/rock_small.png",
            # ... autres chemins ...
        }

        self.load_raw_assets()

    def load_raw_assets(self):
        """Charge toutes les images brutes en mémoire."""
        for id, path in self.ASSET_PATHS.items():
            try:
                # Charger l'image avec un alpha (si elle en a un)
                img = pygame.image.load(path).convert_alpha()
                self.raw_assets[id] = img
            except pygame.error as e:
                print(f"Erreur de chargement de l'image {path}: {e}")
                self.raw_assets[id] = None  # Utiliser None si le chargement échoue

    def get_scaled_image(self, asset_id, tile_size):
        """Retourne l'image mise à l'échelle pour la tile_size donnée, en utilisant un cache."""
        tile_size = int(tile_size)

        if tile_size not in self.scaled_cache:
            self.scaled_cache[tile_size] = {}

        if asset_id in self.scaled_cache[tile_size]:
            return self.scaled_cache[tile_size][asset_id]

        raw_img = self.raw_assets.get(asset_id)

        if raw_img:
            # Mise à l'échelle
            scaled_img = pygame.transform.scale(raw_img, (tile_size, tile_size)).convert_alpha()
            self.scaled_cache[tile_size][asset_id] = scaled_img
            return scaled_img

        return None

    def get_element_ghost_image(self, element_id, tile_size):
        """Crée et retourne une image fantôme (semi-transparente) pour le placement."""
        tile_size = int(tile_size)

        if tile_size not in self.scaled_cache:
            self.scaled_cache[tile_size] = {}

        # Clé spécifique pour l'image fantôme de cet élément à cette taille
        cache_key = f"GHOST_{element_id}"
        if cache_key in self.scaled_cache[tile_size]:
            return self.scaled_cache[tile_size][cache_key]

        # Récupérer l'image normale (mise à l'échelle)
        normal_img = self.get_scaled_image(element_id, tile_size)

        if normal_img:
            ghost_img = normal_img.copy()
            ghost_img.set_alpha(100)  # 100/255 de transparence
            self.scaled_cache[tile_size][cache_key] = ghost_img
            return ghost_img

        return None