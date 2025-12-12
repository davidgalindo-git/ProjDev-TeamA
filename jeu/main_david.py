import pygame
import sys
import globals as G
from ui.minimap.minimap import draw_minimap, handle_minimap_click, handle_minimap_drag
from ui.timer.timer import timer, draw_timer, update_time_from_bar, update_day_from_bar, handle_day_bar_click
from ui.toolbar.toolbar import handle_toolbar_click, draw_toolbar
from todo import get_dimensions, toggle_fullscreen, handle_start_screen_click, draw_start_screen, draw_world

# 1. Initialiser Pygame une seule fois
pygame.init()
pygame.display.set_caption("Créateur d'île - Pygame")

# 3. Charger les images (Maintenant que le mode vidéo est défini)
try:
    # J'ai rétabli l'usage des G.COLORS pour la barre d'outils, car TERRAIN_IMAGES_RAW contient des surfaces.
    # L'erreur de draw_toolbar qui attend une couleur sera corrigée plus bas.
    TERRAIN_IMAGES_RAW = {
        0: pygame.image.load("../assets/water.png").convert_alpha(),
        1: pygame.image.load("../assets/grass.png").convert_alpha(),
        2: pygame.image.load("../assets/dirt.png").convert_alpha(),
        3: pygame.image.load("../assets/sand.png").convert_alpha(),
        4: pygame.image.load("../assets/stone.png").convert_alpha(),
    }
    # J'ai retiré les types 4 (stone/dirt) car ils n'étaient pas définis dans le G.COLORS ni dans TOOLBAR_BUTTONS.
    # Si vous voulez les utiliser, vous devez mettre à jour G.COLORS et TOOLBAR_BUTTONS.
except pygame.error as e:
    print(
        f"Erreur de chargement d'image : Vérifiez l'existence des fichiers dans 'assets/'. Erreur: {e}")
    sys.exit()



# --- Fonction de mise à jour des images redimensionnées (INCHANGÉE) ---




# --- 5. GESTION DE L'ÉCRAN DE DÉMARRAGE (INCHANGÉE) ---

START_BUTTONS = []




while G.running:
    get_dimensions()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            G.running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if G.timer_button.collidepoint(event.pos):
                G.timer_active = not G.timer_active # toggle

            if G.TIME_BAR_RECT.collidepoint(event.pos):
                G.time_bar_dragging = True
                G.timer_active = False  # pause time while scrubbing
                # immediately set time based on click
                rel_x = (event.pos[0] - G.TIME_BAR_RECT.x) / G.TIME_BAR_RECT.width
                G.world_hours = rel_x * 24

            handle_day_bar_click(event.pos)

            # --- Priorité : clic sur la minimap ---
            if G.APP_STATE == "GAME_SCREEN":
                if handle_minimap_click(mouse_pos, G.screen_width, G.grid_bottom_y):
                    # On empêche le reste du code de traiter ce clic
                    G.is_drawing = False
                    G.is_panning = False
                    continue

            if G.APP_STATE == "START_SCREEN":
                handle_start_screen_click(mouse_pos)

            elif G.APP_STATE == "GAME_SCREEN":
                if event.button == 1:  # Clic Gauche (Dessin/ui)
                    if handle_toolbar_click(mouse_pos, G.screen_width, G.grid_bottom_y):
                        G.is_drawing = False
                    elif mouse_pos[1] < G.grid_bottom_y:
                        G.is_drawing = True

                elif event.button == 3:  # Clic Droit (Déplacement)
                    G.is_panning = True
                    last_mouse_pos = mouse_pos

                elif event.button == 4:  # Molette haut (Zoom in)
                    TILE_SIZE = min(64.0, TILE_SIZE + 2.0)

                elif event.button == 5:  # Molette bas (Zoom out)
                    TILE_SIZE = max(4.0, TILE_SIZE - 2.0)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                G.is_drawing = False
                G.is_dragging = False
                G.time_bar_dragging = False
                G.day_bar_dragging = False
                G.minimap_dragging = False
            elif event.button == 3:
                G.is_panning = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if G.time_bar_dragging:
                update_time_from_bar(event.pos)
            if G.day_bar_dragging:
                update_day_from_bar(event.pos)

            # Priorité : si on est en train de drag la minimap → ignorer le reste
            if G.APP_STATE == "GAME_SCREEN" and G.minimap_dragging:
                handle_minimap_drag(mouse_pos, G.screen_width, G.grid_bottom_y)
                continue

            # Panning clic droit
            if G.APP_STATE == "GAME_SCREEN" and G.is_panning:
                dx = mouse_pos[0] - last_mouse_pos[0]
                dy = mouse_pos[1] - last_mouse_pos[1]
                G.camera_x -= dx
                G.camera_y -= dy
                last_mouse_pos = mouse_pos

    # --- LOGIQUE D'AFFICHAGE ---
    G.screen.fill((0, 0, 0))

    if G.APP_STATE == "START_SCREEN":
        draw_start_screen(G.screen_width, G.screen_height)

    elif G.APP_STATE == "GAME_SCREEN":
        # 1. Dessiner le monde (maintenant avec des images) et démarrer timer
        draw_world(G.screen_width, G.grid_bottom_y)

        # 2. Application du Pinceau (Dessin)
        if G.is_drawing:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < G.grid_bottom_y:
                world_x = mouse_x + G.camera_x
                world_y = mouse_y + G.camera_y

                grid_col = int(world_x // TILE_SIZE)
                grid_row = int(world_y // TILE_SIZE)

                if 0 <= grid_col < G.GRID_WIDTH and 0 <= grid_row < G.GRID_HEIGHT:
                    # compute offsets so that we paint an exact CURRENT_BRUSH x CURRENT_BRUSH square
                    N = int(G.CURRENT_BRUSH)
                    start_offset = -(N // 2)
                    # For even sizes this centers slightly up-left which is expected; you can change anchor if you want top-left.
                    for dr in range(start_offset, start_offset + N):
                        for dc in range(start_offset, start_offset + N):
                            r = grid_row + dr
                            c = grid_col + dc
                            if 0 <= r < G.GRID_HEIGHT and 0 <= c < G.GRID_WIDTH:
                                G.world_grid[r][c] = G.CURRENT_TERRAIN
        if G.timer_active:
            G.world_hours, G.world_days, G.display_hours, G.world_minutes = timer(G.world_hours, G.world_days)

        # 3. Dessiner l'ui
        draw_toolbar(G.screen_width, G.grid_bottom_y)
        draw_minimap(G.screen_width, G.grid_bottom_y)
        draw_timer(G.world_days)

    pygame.display.flip()
    G.clock.tick(60)

pygame.quit()
sys.exit()