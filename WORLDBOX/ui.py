import pygame
from config import *

BUTTONS = [
    {"id": 0, "label": "Eau", "color": (52, 152, 219)},
    {"id": 1, "label": "Herbe", "color": (46, 204, 113)},
    {"id": 2, "label": "Terre", "color": (211, 84, 0)},
    {"id": 3, "label": "Sable", "color": (241, 196, 15)}
]

# Nouvelles tailles demandées
BRUSH_SIZES = [1, 2, 4, 8, 16, 32]


def draw_toolbar(screen, current_id, current_brush):
    screen_h = screen.get_height()
    pygame.draw.rect(screen, (40, 40, 40), (0, screen_h - TOOLBAR_HEIGHT, screen.get_width(), TOOLBAR_HEIGHT))

    font = pygame.font.SysFont(None, 22)

    # 1. Dessin des boutons de terrain
    for i, btn in enumerate(BUTTONS):
        x = 10 + i * (BUTTON_WIDTH + 5)
        y = screen_h - TOOLBAR_HEIGHT + 20
        rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        if btn["id"] == current_id:
            pygame.draw.rect(screen, (255, 255, 255), rect.inflate(4, 4))
        pygame.draw.rect(screen, btn["color"], rect)
        screen.blit(font.render(btn["label"], True, (255, 255, 255)), (x + 5, y + 10))

    # 2. Dessin des boutons de taille de pinceau (à droite)
    start_x_brush = 10 + len(BUTTONS) * (BUTTON_WIDTH + 10)
    for i, size in enumerate(BRUSH_SIZES):
        x = start_x_brush + i * 55
        y = screen_h - TOOLBAR_HEIGHT + 20
        rect = pygame.Rect(x, y, 50, BUTTON_HEIGHT)

        # Couleur différente pour distinguer les outils de la taille
        bg_color = (80, 80, 100) if size == current_brush else (60, 60, 60)
        if size == current_brush:
            pygame.draw.rect(screen, (255, 255, 255), rect.inflate(4, 4))

        pygame.draw.rect(screen, bg_color, rect)
        screen.blit(font.render(f"x{size}", True, (255, 255, 255)), (x + 12, y + 10))


def get_toolbar_click(mouse_pos, screen_h):
    """Retourne soit ('terrain', id), soit ('brush', size), soit None."""
    if mouse_pos[1] < screen_h - TOOLBAR_HEIGHT:
        return None

    # Check Terrains
    for i, btn in enumerate(BUTTONS):
        x = 10 + i * (BUTTON_WIDTH + 5)
        rect = pygame.Rect(x, screen_h - TOOLBAR_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        if rect.collidepoint(mouse_pos):
            return ("terrain", btn["id"])

    # Check Brush Sizes
    start_x_brush = 10 + len(BUTTONS) * (BUTTON_WIDTH + 10)
    for i, size in enumerate(BRUSH_SIZES):
        x = start_x_brush + i * 55
        rect = pygame.Rect(x, screen_h - TOOLBAR_HEIGHT + 20, 50, BUTTON_HEIGHT)
        if rect.collidepoint(mouse_pos):
            return ("brush", size)

    return None