import pygame
from world.state import state
from settings import TOOLBAR_HEIGHT, BRUSH_SIZES, COLORS

BUTTON_BASE_WIDTH = 50
BUTTON_GAP = 10
SCROLL_BUTTON_WIDTH = 50

TOOLBAR_BUTTONS = [
    {"type": 0, "label": "Water"},
    {"type": 1, "label": "Grass"},
    {"type": 2, "label": "Dirt"},
    {"type": 3, "label": "Sand"},
    {"type": 4, "label": "Stone"},
    {"type": "BRUSH_1", "label": "x1", "brush": 1},
    {"type": "BRUSH_2", "label": "x2", "brush": 2},
    {"type": "BRUSH_3", "label": "x4", "brush": 4},
    {"type": "BRUSH_4", "label": "x8", "brush": 8},
    {"type": "BRUSH_5", "label": "x16", "brush": 16},
    {"type": "BRUSH_6", "label": "x32", "brush": 32}
]

def handle_toolbar_click(mouse_pos, screen_width, grid_bottom_y):
    if mouse_pos[1] > grid_bottom_y:
        return False
    # scroll not implemented here (kept simple)
    x = mouse_pos[0]
    # simple button mapping by x ranges
    btn_width = BUTTON_BASE_WIDTH + BUTTON_GAP
    idx = int(x // btn_width)
    if 0 <= idx < len(TOOLBAR_BUTTONS):
        btn = TOOLBAR_BUTTONS[idx]
        if "brush" in btn:
            state["current_brush"] = int(btn["brush"])
        else:
            state["current_terrain"] = int(btn["type"])
        return True
    return False

def draw_toolbar(screen, screen_width, grid_bottom_y):
    pygame.draw.rect(screen, (50,50,50), (0, grid_bottom_y, screen_width, TOOLBAR_HEIGHT))
    # draw buttons
    button_y = grid_bottom_y + BUTTON_GAP/2
    for i, btn in enumerate(TOOLBAR_BUTTONS):
        btn_x = SCROLL_BUTTON_WIDTH + (i*(BUTTON_BASE_WIDTH+BUTTON_GAP)) - state.get("scroll_offset",0)
        btn_rect = pygame.Rect(btn_x, button_y, BUTTON_BASE_WIDTH, TOOLBAR_HEIGHT - BUTTON_GAP)
        if "brush" in btn:
            col = (80,80,120)
        else:
            col = COLORS.get(btn["type"], (80,80,80))
        # highlight selected
        is_selected = ("brush" in btn and state["current_brush"]==int(btn.get("brush",0))) or (not "brush" in btn and state["current_terrain"]==btn["type"])
        if is_selected:
            pygame.draw.rect(screen, (200,200,200), btn_rect, border_radius=5)
            inner = btn_rect.inflate(-4,-4)
            pygame.draw.rect(screen, col, inner, border_radius=3)
        else:
            pygame.draw.rect(screen, col, btn_rect, border_radius=5)
        font = pygame.font.SysFont(None, 20)
        text = font.render(str(btn["label"]), True, (255,255,255))
        screen.blit(text, text.get_rect(center=btn_rect.center))
