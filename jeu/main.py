import pygame
import sys
import random # A voir si nécessaire
import math # A voir si nécessaire
import numpy as np # A voir si nécessaire
from opensimplex import OpenSimplex # A voir si nécessaire
import globals as G
from ui.minimap.minimap import draw_minimap, handle_minimap_click, handle_minimap_drag
from ui.timer.timer import timer, draw_timer, update_time_from_bar, update_day_from_bar, handle_day_bar_click
from ui.toolbar.toolbar import handle_toolbar_click, draw_toolbar

from todo import *

clock = pygame.time.Clock()

# --- World Time Simulation ---
timer_active = False


running = True
is_drawing = False
time_bar_dragging = False
day_bar_dragging = False
minimap_dragging = False

while running:
    screen_width, screen_height, grid_bottom_y = get_dimensions()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if G.timer_button.collidepoint(event.pos):
                timer_active = not timer_active # toggle

            if G.TIME_BAR_RECT.collidepoint(event.pos):
                time_bar_dragging = True
                timer_active = False  # pause time while scrubbing
                # immediately set time based on click
                rel_x = (event.pos[0] - G.TIME_BAR_RECT.x) / G.TIME_BAR_RECT.width
                world_hours = rel_x * 24

            handle_day_bar_click(event.pos)

            # --- Priorité : clic sur la minimap ---
            if G.APP_STATE == "GAME_SCREEN":
                if handle_minimap_click(mouse_pos, screen_width, grid_bottom_y):
                    # On empêche le reste du code de traiter ce clic
                    is_drawing = False
                    is_panning = False
                    continue

            if G.APP_STATE == "START_SCREEN":
                handle_start_screen_click(mouse_pos)

            elif G.APP_STATE == "GAME_SCREEN":
                if event.button == 1:  # Clic Gauche (Dessin/ui)
                    if handle_toolbar_click(mouse_pos, screen_width, grid_bottom_y):
                        is_drawing = False
                    elif mouse_pos[1] < grid_bottom_y:
                        is_drawing = True

                elif event.button == 3:  # Clic Droit (Déplacement)
                    is_panning = True
                    last_mouse_pos = mouse_pos

                elif event.button == 4:  # Molette haut (Zoom in)
                    TILE_SIZE = min(64.0, TILE_SIZE + 2.0)

                elif event.button == 5:  # Molette bas (Zoom out)
                    TILE_SIZE = max(4.0, TILE_SIZE - 2.0)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_drawing = False
                is_dragging = False
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
                G.camera_x -= dx
                G.camera_y -= dy
                last_mouse_pos = mouse_pos

    # --- LOGIQUE D'AFFICHAGE ---
    G.screen.fill((0, 0, 0))

    if G.APP_STATE == "START_SCREEN":
        draw_start_screen(screen_width, screen_height)

    elif G.APP_STATE == "GAME_SCREEN":
        # 1. Dessiner le monde (maintenant avec des images) et démarrer timer
        draw_world(screen_width, grid_bottom_y)

        # 2. Application du Pinceau (Dessin)
        if is_drawing:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_y < grid_bottom_y:
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
        if timer_active:
            world_hours, world_days, display_hours, world_minutes = timer(world_hours, world_days)

        # 3. Dessiner l'ui
        draw_toolbar(screen_width, grid_bottom_y)
        draw_minimap(screen_width, grid_bottom_y)
        draw_timer(world_days)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()