import pygame

class AssetManager:
    def __init__(self):
        # 0: Eau, 1: Herbe, 2: Montagne, 5: Rocher
        self.raw_textures = {
            0: self._placeholder((0, 100, 255)),
            1: self._placeholder((50, 200, 50)),
            2: self._placeholder((120, 120, 120)),
            5: self._placeholder((200, 100, 50)) # Objet rocher
        }
        self.cache = {}

    def _placeholder(self, color):
        s = pygame.Surface((64, 64)) # Base HD pour le zoom
        s.fill(color)
        return s

    def get_texture(self, tid, size):
        size = int(size)
        if size <= 0: return None
        key = (tid, size)
        if key not in self.cache:
            raw = self.raw_textures.get(tid)
            if raw:
                self.cache[key] = pygame.transform.scale(raw, (size, size)).convert_alpha()
        return self.cache.get(key)