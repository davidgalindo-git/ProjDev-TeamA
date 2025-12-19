import pygame

class Camera:
    def __init__(self, world_w, world_h, screen_w, screen_h):
        self.world_size = (world_w, world_h) # En tuiles
        self.tile_size = 32.0
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.screen_size = (screen_w, screen_h)

    def world_to_screen(self, world_x, world_y):
        """Prend une position monde (en tuiles) et donne le pixel écran."""
        return (world_x * self.tile_size - self.camera_x,
                world_y * self.tile_size - self.camera_y)

    def screen_to_world(self, scr_x, scr_y):
        """Prend un pixel écran et donne l'index de la tuile (float)."""
        return ((scr_x + self.camera_x) / self.tile_size,
                (scr_y + self.camera_y) / self.tile_size)

    def clamp(self, toolbar_h):
        """Empêche de voir hors de la map."""
        max_x = self.world_size[0] * self.tile_size - self.screen_size[0]
        max_y = self.world_size[1] * self.tile_size - (self.screen_size[1] - toolbar_h)
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))