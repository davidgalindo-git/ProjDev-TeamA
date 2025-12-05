import pygame


def draw_toolbar(
    screen,
    world,
    scroll_offset,
    screen_width,
    grid_bottom_y,
    font,
    buttons,
    colors,
    current_terrain,
    current_brush
):
    """Dessine la barre d'outils et les boutons de brush."""
    TOOLBAR_HEIGHT = 80
    BUTTON_BASE_WIDTH = 60
    BUTTON_HEIGHT = 60
    BUTTON_GAP = 10
    SCROLL_BUTTON_WIDTH = 40

    toolbar_rect = pygame.Rect(0, grid_bottom_y, screen_width, TOOLBAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), toolbar_rect)

    # Zone où les boutons sont visibles
    button_area_rect = pygame.Rect(
        SCROLL_BUTTON_WIDTH,
        grid_bottom_y,
        screen_width - 2 * SCROLL_BUTTON_WIDTH,
        TOOLBAR_HEIGHT
    )
    screen.set_clip(button_area_rect)

    button_y = grid_bottom_y + BUTTON_GAP / 2

    for i, btn in enumerate(buttons):
        btn_x_absolute = SCROLL_BUTTON_WIDTH + (i * (BUTTON_BASE_WIDTH + BUTTON_GAP)) - scroll_offset
        btn_rect = pygame.Rect(btn_x_absolute, button_y, BUTTON_BASE_WIDTH, BUTTON_HEIGHT)

        # Couleur
        if "brush" in btn:
            btn_color = (80, 80, 120)
        else:
            btn_color = colors.get(btn["type"], (50, 50, 50))

        is_selected = (
            ("brush" in btn and int(btn["brush"]) == current_brush)
            or ("type" in btn and btn["type"] == current_terrain)
        )

        if is_selected:
            pygame.draw.rect(screen, (200, 200, 200), btn_rect, border_radius=5)
            inner_rect = btn_rect.inflate(-4, -4)
            pygame.draw.rect(screen, btn_color, inner_rect, border_radius=3)
        else:
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)

        # Label
        text_surface = font.render(str(btn["label"]), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=btn_rect.center)
        screen.blit(text_surface, text_rect)

    screen.set_clip(None)


def handle_toolbar_click(
    mouse_pos,
    scroll_offset,
    screen_width,
    grid_bottom_y,
    buttons,
    current_terrain,
    current_brush
):
    """Gère le clic sur la barre d'outils."""
    TOOLBAR_HEIGHT = 80
    BUTTON_BASE_WIDTH = 60
    BUTTON_GAP = 10
    SCROLL_BUTTON_WIDTH = 40

    if mouse_pos[1] < grid_bottom_y:
        return scroll_offset, current_terrain, current_brush, False

    # Flèche gauche
    left_rect = pygame.Rect(0, grid_bottom_y, SCROLL_BUTTON_WIDTH, TOOLBAR_HEIGHT)
    if left_rect.collidepoint(mouse_pos):
        scroll_offset = max(0, scroll_offset - (BUTTON_BASE_WIDTH + BUTTON_GAP))
        return scroll_offset, current_terrain, current_brush, True

    # Flèche droite
    right_rect = pygame.Rect(screen_width - SCROLL_BUTTON_WIDTH, grid_bottom_y, SCROLL_BUTTON_WIDTH, TOOLBAR_HEIGHT)
    if right_rect.collidepoint(mouse_pos):
        total_w = (BUTTON_BASE_WIDTH + BUTTON_GAP) * len(buttons)
        avail_w = screen_width - 2 * SCROLL_BUTTON_WIDTH - BUTTON_GAP
        max_offset = max(0, total_w - avail_w)
        scroll_offset = min(max_offset, scroll_offset + (BUTTON_BASE_WIDTH + BUTTON_GAP))
        return scroll_offset, current_terrain, current_brush, True

    # Clic sur un bouton
    corrected_x = mouse_pos[0] + scroll_offset - SCROLL_BUTTON_WIDTH
    btn_index = int(corrected_x // (BUTTON_BASE_WIDTH + BUTTON_GAP))

    if 0 <= btn_index < len(buttons):
        local_x = corrected_x - btn_index * (BUTTON_BASE_WIDTH + BUTTON_GAP)
        if local_x < BUTTON_BASE_WIDTH:
            btn = buttons[btn_index]

            if "brush" in btn:
                current_brush = int(btn["brush"])
            else:
                current_terrain = btn["type"]

            return scroll_offset, current_terrain, current_brush, True

    return scroll_offset, current_terrain, current_brush, False
