import pygame
import jeu.globals as G

# --- 1. GESTION DES CLICS ---

def handle_toolbar_click(mouse_pos, world_instance, scroll_offset_val, get_dimensions_func):
    """
    Gère le clic sur la barre d'outils. Modifie world_instance en place.
    Retourne (nouveau_scroll_offset, True/False si cliqué).
    """
    # Récupération des dimensions via la fonction passée en argument
    screen_width, screen_height, grid_bottom_y = get_dimensions_func()

    if mouse_pos[1] > grid_bottom_y:

        # 1. Gérer les flèches de défilement
        left_arrow_rect = pygame.Rect(0, grid_bottom_y, G.SCROLL_BUTTON_WIDTH, G.TOOLBAR_HEIGHT)
        right_arrow_rect = pygame.Rect(screen_width - G.SCROLL_BUTTON_WIDTH, grid_bottom_y, G.SCROLL_BUTTON_WIDTH,
                                       G.TOOLBAR_HEIGHT)

        # Clic sur la flèche gauche
        if left_arrow_rect.collidepoint(mouse_pos):
            scroll_offset_val = max(0, scroll_offset_val - (G.BUTTON_BASE_WIDTH + G.BUTTON_GAP) * 2)
            return scroll_offset_val, True

        # Clic sur la flèche droite
        if right_arrow_rect.collidepoint(mouse_pos):
            total_button_width = (G.BUTTON_BASE_WIDTH + G.BUTTON_GAP) * len(G.TOOLBAR_BUTTONS)
            available_width = screen_width - 2 * G.SCROLL_BUTTON_WIDTH - G.BUTTON_GAP
            max_offset = max(0, total_button_width - available_width)

            scroll_offset_val = min(max_offset, scroll_offset_val + (G.BUTTON_BASE_WIDTH + G.BUTTON_GAP) * 2)
            return scroll_offset_val, True

        # 2. Gérer les boutons d'outils
        corrected_x = mouse_pos[0] + scroll_offset_val - G.SCROLL_BUTTON_WIDTH
        btn_index = int(corrected_x // (G.BUTTON_BASE_WIDTH + G.BUTTON_GAP))

        if 0 <= btn_index < len(G.TOOLBAR_BUTTONS):
            btn_x_start_in_corrected_area = btn_index * (G.BUTTON_BASE_WIDTH + G.BUTTON_GAP)
            click_x_in_button_space = corrected_x - btn_x_start_in_corrected_area

            if click_x_in_button_space < G.BUTTON_BASE_WIDTH:
                btn = G.TOOLBAR_BUTTONS[btn_index]

                # Mise à jour de l'instance World
                if "brush" in btn:
                    world_instance.current_brush_size = int(btn["brush"])
                    world_instance.current_terrain = -1
                else:
                    world_instance.current_terrain = btn["type"]

                return scroll_offset_val, True

    return scroll_offset_val, False


# --- 2. FONCTION DE DESSIN ---

def draw_toolbar(screen_surface, world_instance, scroll_offset_val, get_dimensions_func, label_font):
    """Dessine la barre d'outils en utilisant les arguments passés."""
    screen_width, screen_height, grid_bottom_y = get_dimensions_func()

    # Dessiner le fond de la toolbar
    toolbar_rect = pygame.Rect(0, grid_bottom_y, screen_width, G.TOOLBAR_HEIGHT)
    pygame.draw.rect(screen_surface, (50, 50, 50), toolbar_rect)

    # 1. Dessiner les flèches de défilement
    left_arrow_rect = pygame.Rect(0, grid_bottom_y, G.SCROLL_BUTTON_WIDTH, G.TOOLBAR_HEIGHT)
    pygame.draw.rect(screen_surface, (80, 80, 80), left_arrow_rect)
    right_arrow_rect = pygame.Rect(screen_width - G.SCROLL_BUTTON_WIDTH, grid_bottom_y, G.SCROLL_BUTTON_WIDTH,
                                   G.TOOLBAR_HEIGHT)
    pygame.draw.rect(screen_surface, (80, 80, 80), right_arrow_rect)

    # Dessin des triangles (simples)
    pygame.draw.polygon(screen_surface, (255, 255, 255), [
        (left_arrow_rect.centerx + 10, left_arrow_rect.centery - 10),
        (left_arrow_rect.centerx - 10, left_arrow_rect.centery),
        (left_arrow_rect.centerx + 10, left_arrow_rect.centery + 10)
    ])
    pygame.draw.polygon(screen_surface, (255, 255, 255), [
        (right_arrow_rect.centerx - 10, right_arrow_rect.centery - 10),
        (right_arrow_rect.centerx + 10, right_arrow_rect.centery),
        (right_arrow_rect.centerx - 10, right_arrow_rect.centery + 10)
    ])

    # 2. Dessiner la zone des boutons (clipping pour le défilement)
    button_area_rect = pygame.Rect(G.SCROLL_BUTTON_WIDTH, grid_bottom_y, screen_width - 2 * G.SCROLL_BUTTON_WIDTH,
                                   G.TOOLBAR_HEIGHT)
    screen_surface.set_clip(button_area_rect)

    button_y = grid_bottom_y + G.BUTTON_GAP / 2

    # 3. Dessiner chaque bouton
    for i, btn in enumerate(G.TOOLBAR_BUTTONS):
        btn_x_absolute = G.SCROLL_BUTTON_WIDTH + (i * (G.BUTTON_BASE_WIDTH + G.BUTTON_GAP)) - scroll_offset_val
        btn_rect = pygame.Rect(btn_x_absolute, button_y, G.BUTTON_BASE_WIDTH, G.BUTTON_HEIGHT)

        # Définition des couleurs et de l'état sélectionné
        is_selected = False
        if "brush" in btn:
            btn_color = (80, 80, 120)
            if int(btn["brush"]) == int(world_instance.current_brush_size):
                is_selected = True
        else:
            btn_color = G.COLORS.get(btn["type"], (50, 50, 50))
            if btn["type"] == world_instance.current_terrain:
                is_selected = True

        # Dessin du bouton
        if is_selected:
            pygame.draw.rect(screen_surface, (200, 200, 200), btn_rect, border_radius=5)
            inner_rect = btn_rect.inflate(-4, -4)
            pygame.draw.rect(screen_surface, btn_color, inner_rect, border_radius=3)
        else:
            pygame.draw.rect(screen_surface, btn_color, btn_rect, border_radius=5)

        # Dessin du texte
        text_label = str(btn["label"])
        text_surface = label_font.render(text_label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=btn_rect.center)
        screen_surface.blit(text_surface, text_rect)

    # Retire le clipping après avoir dessiné les boutons
    screen_surface.set_clip(None)