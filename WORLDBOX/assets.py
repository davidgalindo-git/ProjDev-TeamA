import pygame
import random


class AssetManager:
    def __init__(self):
        # liste ID animé. Seul l'id 0 est animé (eau)
        self.animated_ids = [0]
        # Initialiser les textures de base
        self.textures = {
            0: self._generate_animated_asset((0, 100, 255), "water"),
            1: self._generate_static_asset((50, 200, 50), "grass"),
            2: self._generate_static_asset((120, 120, 120), "mountain"),
            3: self._generate_static_asset((240, 230, 140), "sand"),
            4: self._generate_static_asset((100, 100, 100), "rock"),
            5: self._generate_static_asset((40, 140, 40), "tree")
        }
        self.cache = {}
        # stocke les images 1 fois afin d'améliorer les performances.
        # évite de calculer plusieurs fois un même objet

    def _generate_static_asset(self, base_color, asset_type):
        # taille plus grande pour l'arbre(64 de large, 96 de haut)
        # SRCALPHA permet de mettre de la transparence en dessous des arbres afin de retirer le noir ou blanc
        w, h = (64, 96) if asset_type == "tree" else (32, 32)
        s = pygame.Surface((w, h), pygame.SRCALPHA)

        if asset_type == "tree":
            pygame.draw.rect(s, (70, 40, 20), (28, 70, 8, 20))  # Tronc
            pygame.draw.circle(s, (30, 80, 30), (32, 45), 30)  # Feuillage
            pygame.draw.circle(s, base_color, (30, 40), 25)

        elif asset_type == "rock":
            # apparence du rocher
            pts = [(5, 25), (10, 10), (22, 10), (28, 25), (16, 30)]
            # Couleurs
            pygame.draw.polygon(s, (80, 80, 80), pts)
            # points => les sommets du rochers.
            pygame.draw.polygon(s, (120, 120, 120), [(10, 18), (20, 18), (15, 12)])
        else:
            # récupère les assets mountain, grass, sand pour ajouter des touches de textures aléatoires à chaque lancement
            s.fill(base_color)
            for _ in range(15):
                # cette partie récupère les couleurs de base afin de prendre les couleurs proches pour créer des textures
                c = [max(0, min(255, x + random.randint(-15, 15))) for x in base_color]
                pygame.draw.rect(s, c, (random.randint(0, 31), random.randint(0, 31), 2, 2))
        return [s, s, s]

    def _generate_animated_asset(self, base_color, asset_type):
        frames = []
        for i in range(3):
            s = pygame.Surface((32, 32))
            s.fill(base_color)
            if asset_type == "water":
                # Retour de l'animation de vagues qui bougent
                foam = (180, 220, 255)
                for v in range(2):
                    # chaque frame, déplace la position des vagues vers la droite
                    mx = (i * 6 + v * 16) % 32  # Décalage horizontal basé sur la frame
                    # * 16 => espacement de 16 pixels des vagues pour éviter les chevauchements
                    # % 32 => si la vague se rapproche trop du bord, il va directement repartir vers la gauche
                    my = 10 + v * 12
                    pts = [(mx, my), (mx + 4, my + 2), (mx + 8, my)]
                    # mx => définit les 3 points pour afficher les vaguelettes
                    if pts[0][0] < pts[2][0]:
                        # sécurité pour éviter
                        pygame.draw.lines(s, foam, False, pts, 2)
            frames.append(s)
        return frames

    def get_texture(self, tid, size, frame_index):
        #force à récupérer des pixels entier pour éviter des bugs visuels
        size = int(size)
        if size <= 0: return None
        # sécurité anti crash. envoie None si la taille esst de zéro ou négative (dézoom)
        idx = frame_index if tid in self.animated_ids else 0
        # vérifie si l objet est l'eau. si oui, affichera l'animation. sinon garde la texture de base
        key = (tid, size, idx)


        if key not in self.cache:
            raw = self.textures.get(tid, self.textures[1])[idx]
            # calcul pour conserver les tailles d'origines
            w_ratio = raw.get_width() / 32
            h_ratio = raw.get_height() / 32

            scaled = pygame.transform.scale(raw, (int(size * w_ratio), int(size * h_ratio)))
            #permet d'afficher des centaines d'arbre sans baissé en framerate
            self.cache[key] = scaled.convert_alpha()

        return self.cache.get(key)