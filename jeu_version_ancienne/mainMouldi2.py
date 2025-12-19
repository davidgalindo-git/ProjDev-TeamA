# Fichier: main.py

import pygame
import sys
import globals as G  # Contient G.screen, G.APP_STATE, G.initial_grid, etc.
from ui.minimap.minimap import draw_minimap, handle_minimap_click, handle_minimap_drag
from ui.timer.timer import timer, draw_timer, update_time_from_bar, update_day_from_bar, handle_day_bar_click
from worldManagement import World  # Import corrigé (world_management)
from imageLoader import ImageManager  # Import corrigé (images)
from toolbar_cg import ToolbarManager  # Import corrigé (toolbar)
from draw_world import draw_elements, draw_brush_preview   # NOUVEAU: Pour le rendu du monde

from todo import *  # Assurez-vous que get_dimensions(), toggle_fullscreen(), etc. sont ici

clock = pygame.time.Clock()

# --- INITIALISATION DES CLASSES REFECTORÉES ---
timer_active = False

# world gère les données, la caméra, et le zoom (remplace TILE_SIZE, G.camera_x, G.world_grid)
world = World(initial_grid=G.initial_grid)
# imageManager gère les assets redimensionnés (remplace TERRAIN_IMAGES_RAW/SCALED)
image_manager = ImageManager()

ui_font = pygame.font.Font(None, 24)
# toolbar_manager gère l'UI du bas et le choix du pinceau/terrain
toolbar_manager = ToolbarManager(ui_font)

running = True
is_drawing = False
is_panning = False  # Variable manquante dans l'original
time_bar_dragging = False
day_bar_dragging = False
minimap_dragging = False
last_mouse_pos = (0, 0)  # Pour le panning

while running:
    # Récupération des dimensions (doit inclure la hauteur de l'écran)
    screen_width, screen_height, grid_bottom_y = get_dimensions()

    # S'assurer que les bornes de la caméra et du zoom sont respectées
    world.adjust_camera(screen_width, screen_height)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # ... (Logique Timer et Day Bar inchangée) ...
            if G.timer_button.collidepoint(event.pos):
                timer_active = not timer_active

            if G.TIME_BAR_RECT.collidepoint(event.pos):
                time_bar_dragging = True
                timer_active = False
                rel_x = (event.pos[0] - G.TIME_BAR_RECT.x) / G.TIME_BAR_RECT.width
                # world_hours doit être accessible dans G ou initialisé
                world_hours = rel_x * 24

            handle_day_bar_click(event.pos)

            # --- Priorité : clic sur la minimap ---
            if G.APP_STATE == "GAME_SCREEN":
                if handle_minimap_click(mouse_pos, screen_width, grid_bottom_y):
                    is_drawing = False
                    is_panning = False
                    continue

            if G.APP_STATE == "START_SCREEN":
                handle_start_screen_click(mouse_pos)

            elif G.APP_STATE == "GAME_SCREEN":
                if event.button == 1:  # Clic Gauche (Dessin/ui)
                    # DELEGATION AU TOOLBAR MANAGER
                    if toolbar_manager.handle_click(mouse_pos, screen_width, grid_bottom_y, world):
                        is_drawing = False  # Le clic a été consommé par la toolbar
                    elif mouse_pos[1] < grid_bottom_y:
                        # On est dans la grille, activation du mode dessin/placement
                        is_drawing = True

                        # LOGIQUE D'ELEMENTS (pour le placement en 1-clic : Rocher/G.Rocher)
                        if world.current_terrain >= 5:
                            world_x = mouse_pos[0] + world.camera_x
                            world_y = mouse_pos[1] + world.camera_y
                            world.place_element(world_x, world_y)
                            is_drawing = False  # On ne dessine pas en continu pour les éléments

                elif event.button == 3:  # Clic Droit (Déplacement)
                    # Clic droit sur l'élément => tenter d'effacer
                    if world.current_terrain >= 5 and mouse_pos[1] < grid_bottom_y:
                        world_x = mouse_pos[0] + world.camera_x
                        world_y = mouse_pos[1] + world.camera_y
                        world.erase_element(world_x, world_y)
                    else:
                        is_panning = True
                        last_mouse_pos = mouse_pos

                elif event.button == 4:  # Molette haut (Zoom in)
                    # DELEGATION AU WORLD MANAGER
                    world.zoom_in()

                elif event.button == 5:  # Molette bas (Zoom out)
                    # DELEGATION AU WORLD MANAGER
                    world.zoom_out()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_drawing = False
                # is_dragging = False # Variable non définie
                time_bar_dragging = False
                day_bar_dragging = False
                minimap_dragging = False
            elif event.button == 3:
                is_panning = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if time_bar_dragging:
                update_time_from_bar(event.pos)
            if day_bar_dragging:
                update_day_from_bar(event.pos)

            # Priorité : si on est en train de drag la minimap → ignorer le reste
            if G.APP_STATE == "GAME_SCREEN" and minimap_dragging:
                handle_minimap_drag(mouse_pos, screen_width, grid_bottom_y)
                continue

            # Panning clic droit
            if G.APP_STATE == "GAME_SCREEN" and is_panning:
                dx = mouse_pos[0] - last_mouse_pos[0]
                dy = mouse_pos[1] - last_mouse_pos[1]
                # DELEGATION AU WORLD MANAGER
                world.pan(dx, dy)
                last_mouse_pos = mouse_pos

    # --- LOGIQUE D'AFFICHAGE ---
    G.screen.fill((0, 0, 0))

    if G.APP_STATE == "START_SCREEN":
        draw_start_screen(screen_width, screen_height)

    elif G.APP_STATE == "GAME_SCREEN":
        # 1. Dessiner le monde et démarrer timer
        # DELEGATION AU RENDERER
        draw_world(G.screen, world, image_manager)
        draw_elements(G.screen, world, image_manager, screen_width, screen_height)

        # 2. Application du Pinceau (Dessin de Terrain continu)
        if is_drawing and world.current_terrain <= 4:  # Terrain seulement (ID < 5)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < grid_bottom_y:
                world_x = mouse_x + world.camera_x
                world_y = mouse_y + world.camera_y
                # DELEGATION AU WORLD MANAGER
                world.paint_terrain(world_x, world_y)

        if timer_active:
            # world_hours, world_days doivent être initialisés ou gérés globalement
            world_hours, world_days, display_hours, world_minutes = timer(world_hours, world_days)

        # 3. Dessiner l'ui
        # DELEGATION AU TOOLBAR MANAGER
        toolbar_manager.draw_toolbar(G.screen, world, screen_width, grid_bottom_y)

        # Dessiner l'aperçu du pinceau (Ghost image)
        if mouse_pos[1] < grid_bottom_y:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Pour le Terrain (pinceau carré)
            if world.current_terrain <= 4:
                draw_brush_preview(G.screen, world, mouse_x, mouse_y, grid_bottom_y)

            # Pour les Éléments (aperçu 1x1 ou 4x4) - À IMPLEMENTER

        draw_minimap(screen_width, grid_bottom_y)
        draw_timer(world_days)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

# Note : Les fichiers 'world_management.py', 'images.py', et 'toolbar.py' sont considérés 
# comme corrects d'après la révision précédente.