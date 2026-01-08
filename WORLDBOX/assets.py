import pygame
import random


class AssetManager:
    def __init__(self):
        # On définit les IDs qui doivent bouger (uniquement l'eau ici)
        self.animated_ids = [0]
        self.textures = {
            0: self._generate_animated_asset((0, 100, 255), "water"),
            1: self._generate_static_asset((50, 200, 50)),  # Herbe fixe
            2: self._generate_static_asset((120, 120, 120)),  # Montagne fixe
            3: self._generate_static_asset((240, 230, 140))  # Sable fixe
        }
        self.cache = {}

    def _generate_static_asset(self, base_color):
        """Génère une seule frame pour les assets qui ne bougent pas."""
        s = pygame.Surface((32, 32))
        s.fill(base_color)
        # On ajoute un peu de grain pour que ce soit moins "plat"
        for _ in range(20):
            c = [max(0, min(255, x + random.randint(-10, 10))) for x in base_color]
            pygame.draw.rect(s, c, (random.randint(0, 30), random.randint(0, 30), 2, 2))
        return [s, s, s]  # On renvoie 3 fois la même image pour garder la logique d'index

    def _generate_animated_asset(self, base_color, asset_type):
        frames = []
        for i in range(3):
            s = pygame.Surface((32, 32))
            s.fill(base_color)

            # Effet de vagues pour l'eau
            if asset_type == "water":
                # Couleur de l'écume (bleu très clair)
                foam_color = (200, 230, 255)
                # On dessine 2 petites vagues par tile
                for v in range(2):
                    offset_x = (i * 6) + (v * 15)  # Décalage horizontal selon la frame
                    y = 10 + (v * 12)
                    # On dessine une vague en "V" très aplati ou en arc
                    points = [
                        ((offset_x) % 32, y),
                        ((offset_x + 4) % 32, y + 2),
                        ((offset_x + 8) % 32, y)
                    ]
                    # On dessine la ligne de la vague
                    if points[0][0] < points[2][0]:  # Évite les bugs de bordure de tile
                        pygame.draw.lines(s, foam_color, False, points, 2)

            frames.append(s)
        return frames

    def get_texture(self, tid, size, frame_index):
        size = int(size)
        if size <= 0: return None

        # Si le terrain n'est pas animé, on force la frame 0
        current_frame = frame_index if tid in self.animated_ids else 0

        key = (tid, size, current_frame)
        if key not in self.cache:
            frames = self.textures.get(tid)
            if frames:
                raw = frames[current_frame]
                self.cache[key] = pygame.transform.scale(raw, (size, size)).convert_alpha()
        return self.cache.get(key)