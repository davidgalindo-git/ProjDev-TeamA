import pygame
import random
import math

class NPC:
    def __init__(self, x_tile, y_tile):
        # Position en "coordonnées monde" (pixels)
        self.pos = pygame.Vector2(x_tile * 32, y_tile * 32)
        self.target_pos = None
        self.speed = 1.5

    def is_water(self, check_pos, world):
        """Vérifie si un point précis est de l'eau."""
        gx = int(check_pos.x // world.tile_size)
        gy = int(check_pos.y // world.tile_size)
        if 0 <= gy < len(world.grid) and 0 <= gx < len(world.grid[0]):
            return world.grid[gy][gx] == 0 # ID 0 = Eau
        return True

    def update(self, world):
        # Si pas de cible ou cible dans l'eau (car le joueur a pu peindre de l'eau entre temps)
        if self.target_pos is None or self.is_water(self.target_pos, world):
            self.pick_target(world)

        # Déplacement
        direction = self.target_pos - self.pos
        if direction.length() > 5:
            # Anticipation : on regarde un peu plus loin devant
            look_ahead = self.pos + direction.normalize() * 30
            if self.is_water(look_ahead, world):
                self.pick_target(world) # On change de direction si obstacle eau
            else:
                self.pos += direction.normalize() * self.speed
        else:
            self.target_pos = None

    def pick_target(self, world):
        """Cherche un point de terre ferme aléatoire autour du NPC."""
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(100, 300)
            test_pos = self.pos + pygame.Vector2(math.cos(angle) * dist, math.sin(angle) * dist)
            if not self.is_water(test_pos, world):
                self.target_pos = test_pos
                return

    def draw(self, screen, world):
        """Affiche le perso en tenant compte de la caméra."""
        screen_x = self.pos.x - world.camera_x
        screen_y = self.pos.y - world.camera_y
        # On ne dessine que s'il est sur l'écran
        if -20 < screen_x < screen.get_width() + 20 and -20 < screen_y < screen.get_height() + 20:
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 10) # Corps
            pygame.draw.circle(screen, (200, 0, 0), (int(screen_x), int(screen_y)), 8)      # Détail