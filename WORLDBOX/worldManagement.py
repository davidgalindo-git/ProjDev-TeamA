import numpy as np
import random
import math
from opensimplex import OpenSimplex
from config import *

class World:
    def __init__(self, mode="vide"):
        self.tile_size = INIT_TILE_SIZE
        self.camera_x, self.camera_y = 0.0, 0.0

        if mode == "aleatoire":
            # CORRECTION : Le nom de la fonction appelée doit correspondre à la définition plus bas
            self.grid = self._generate_logical_island()
        else:
            self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int).tolist()

    def _generate_logical_island(self):
        """Génère l'île avec les formes fluides et les couleurs demandées."""
        seed = random.randint(0, 10000)
        gen = OpenSimplex(seed=seed)

        SCALE = 20.0
        new_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)

        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                # 1. Bruit de base
                noise_val = (gen.noise2(c / SCALE, r / SCALE) + 1) / 2

                # 2. Masque de distance (Falloff) pour centrer l'île
                nx, ny = 2 * c / GRID_WIDTH - 1, 2 * r / GRID_HEIGHT - 1
                dist = math.sqrt(nx ** 2 + ny ** 2)
                # Puissance 2.5 pour une chute de terrain nette sur les bords
                falloff = 1.0 - pow(dist, 2.5)

                val = noise_val * max(0, falloff)

                # 3. Attribution des IDs de terrain (Logique de l'image)
                if val > 0.45:  # Intérieur de l'île
                    if random.random() < 0.12:
                        new_grid[r, c] = 2  # Brun Terre (petites taches)
                    else:
                        new_grid[r, c] = 1  # Vert Gazon (Majoritaire)
                elif val > 0.38:
                    new_grid[r, c] = 3  # Jaune Sable (Bordure fine)
                else:
                    new_grid[r, c] = 0  # Bleu Mer

        return new_grid.tolist()