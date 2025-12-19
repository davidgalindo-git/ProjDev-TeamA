# Fichier: toolbar.py

import pygame

# Constantes de la barre d'outils (à synchroniser avec World.TOOLBAR_HEIGHT)
TOOLBAR_HEIGHT = 80
BUTTON_BASE_WIDTH = 60
BUTTON_HEIGHT = 60
BUTTON_GAP = 10
SCROLL_BUTTON_WIDTH = 40

# Structure de données des boutons (exemple pour l'initialisation)
DEFAULT_BUTTONS = [
    {"label": "Eau", "type": 0},
    {"label": "Terre", "type": 1},
    {"label": "Mont.", "type": 2},
    {"label": "Plage", "type": 3},
    {"label": "P1", "brush": 1},
    {"label": "P2", "brush": 2},
    {"label": "P4", "brush": 4},
    {"label": "Rocher", "type": 5}, # ID 5 = Element 1x1
    {"label": "G.Roch", "type": 6}, # ID 6 = Element 4x4
    # ... autres boutons
]

TERRAIN_COLORS = {
    0: (0, 0, 100), # Eau
    1: (0, 100, 0), # Terre
    2: (100, 100, 100), # Montagne
    3: (200, 200, 150), # Plage
    5: (150, 150, 150), # Rocher
    6: (150, 150, 150), # G.Rocher
}


class ToolbarManager:
    """Gère l'affichage et l'interaction de la barre d'outils."""
    def __init__(self, font):
        self.font = font
        self.buttons = DEFAULT_BUTTONS
        self.colors = TERRAIN_COLORS
        self.scroll_offset = 0

    def draw_toolbar(self, screen, world, screen_width, grid_bottom_y):
        """Dessine la barre d'outils et les boutons de brush."""
        toolbar_rect = pygame.Rect(0, grid_bottom_y, screen_width, TOOLBAR_HEIGHT)
        pygame.draw.rect(screen, (50, 50, 50), toolbar_rect)

        # Zone où les boutons sont visibles (clipping)
        button_area_rect = pygame.Rect(
            SCROLL_BUTTON_WIDTH,
            grid_bottom_y,
            screen_width - 2 * SCROLL_BUTTON_WIDTH,
            TOOLBAR_HEIGHT
        )
        screen.set_clip(button_area_rect)

        button_y = grid_bottom_y + BUTTON_GAP / 2

        for i, btn in enumerate(self.buttons):
            btn_x_absolute = SCROLL_BUTTON_WIDTH + (i * (BUTTON_BASE_WIDTH + BUTTON_GAP)) - self.scroll_offset
            btn_rect = pygame.Rect(btn_x_absolute, button_y, BUTTON_BASE_WIDTH, BUTTON_HEIGHT)

            # Couleur du bouton
            if "brush" in btn:
                btn_color = (80, 80, 120)
            else:
                btn_color = self.colors.get(btn["type"], (50, 50, 50))

            # Sélection
            is_selected = (
                ("brush" in btn and int(btn["brush"]) == world.current_brush_size)
                or ("type" in btn and btn["type"] == world.current_terrain)
            )

            if is_selected:
                pygame.draw.rect(screen, (200, 200, 200), btn_rect, border_radius=5)
                inner_rect = btn_rect.inflate(-4, -4)
                pygame.draw.rect(screen, btn_color, inner_rect, border_radius=3)
            else:
                pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)

            # Label
            text_surface = self.font.render(str(btn["label"]), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=btn_rect.center)
            screen.blit(text_surface, text_rect)

        screen.set_clip(None)

    def handle_click(self, mouse_pos, screen_width, grid_bottom_y, world):
        """Gère le clic sur la barre d'outils. Met à jour world.current_terrain/brush_size."""

        if mouse_pos[1] < grid_bottom_y:
            return False # Pas de clic sur la barre d'outils

        # Flèche gauche
        left_rect = pygame.Rect(0, grid_bottom_y, SCROLL_BUTTON_WIDTH, TOOLBAR_HEIGHT)
        if left_rect.collidepoint(mouse_pos):
            self.scroll_offset = max(0, self.scroll_offset - (BUTTON_BASE_WIDTH + BUTTON_GAP))
            return True

        # Flèche droite
        right_rect = pygame.Rect(screen_width - SCROLL_BUTTON_WIDTH, grid_bottom_y, SCROLL_BUTTON_WIDTH, TOOLBAR_HEIGHT)
        if right_rect.collidepoint(mouse_pos):
            total_w = (BUTTON_BASE_WIDTH + BUTTON_GAP) * len(self.buttons)
            avail_w = screen_width - 2 * SCROLL_BUTTON_WIDTH - BUTTON_GAP
            max_offset = max(0, total_w - avail_w)
            self.scroll_offset = min(max_offset, self.scroll_offset + (BUTTON_BASE_WIDTH + BUTTON_GAP))
            return True

        # Clic sur un bouton
        corrected_x = mouse_pos[0] + self.scroll_offset - SCROLL_BUTTON_WIDTH
        btn_index = int(corrected_x // (BUTTON_BASE_WIDTH + BUTTON_GAP))

        if 0 <= btn_index < len(self.buttons):
            local_x = corrected_x - btn_index * (BUTTON_BASE_WIDTH + BUTTON_GAP)
            if local_x < BUTTON_BASE_WIDTH:
                btn = self.buttons[btn_index]

                if "brush" in btn:
                    world.current_brush_size = int(btn["brush"])
                else:
                    world.current_terrain = btn["type"]

                return True

        return False