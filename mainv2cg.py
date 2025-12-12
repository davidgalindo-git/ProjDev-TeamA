import pygame, sys

from config_cg import *
from assets.loader_cg import load_raw_assets, scale_assets
from world.world_state_cg import WorldState
from world.generation_cg import generate_random_world
from jeu.draw_world import draw_world
from jeu.toolbar_cg import draw_toolbar, handle_toolbar_click
from ui.minimap_cg import draw_minimap, handle_minimap_click, handle_minimap_drag
from ui.start_screen_cg import draw_start_screen, handle_start_screen_click

pygame.init()
screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT))

# --- Fonts ---
font = pygame.font.SysFont("Arial", 24)
title_font = pygame.font.SysFont("Arial", 48, bold=True)

# --- World ---
world = WorldState()
raw_assets = load_raw_assets()
scaled_assets = scale_assets(raw_assets, world.tile_size)

APP_STATE = "START"
clock = pygame.time.Clock()

scroll_offset = 0
is_drawing = False
is_panning = False
minimap_dragging = False
drag_offset = (0, 0)
last_mouse = (0, 0)

# Buttons are built each frame of START state, so init to empty
START_BUTTONS = []

while True:
    mouse_pos = pygame.mouse.get_pos()
    scr_w, scr_h = screen.get_size()
    grid_bottom = scr_h - TOOLBAR_HEIGHT

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # --- Start Screen Click ---
        if APP_STATE == "START":
            if event.type == pygame.MOUSEBUTTONDOWN:
                state_change = handle_start_screen_click(
                    mouse_pos,
                    START_BUTTONS,
                    world.grid,
                    GRID_WIDTH,
                    GRID_HEIGHT,
                    generate_random_world
                )
                if state_change:
                    APP_STATE = state_change
            continue

        # -------------------------------------
        #         GAME SCREEN EVENTS
        # -------------------------------------

        # --- Minimap : début clic ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = handle_minimap_click(
                mouse_pos,
                screen,
                world.grid,
                world.camera_x,
                world.camera_y,
                scr_w,
                grid_bottom,
                world.tile_size,
                TOOLBAR_HEIGHT
            )

            if result:
                if result[0] == "DRAG_START":
                    minimap_dragging = True
                    drag_offset = result[1]
                elif result[0] == "MOVE":
                    _, cx, cy = result
                    world.camera_x = cx
                    world.camera_y = cy

        # --- Minimap drag ---
        if event.type == pygame.MOUSEMOTION and minimap_dragging:
            cx, cy = handle_minimap_drag(
                mouse_pos,
                drag_offset,
                screen,
                world.grid,
                world.tile_size,
                TOOLBAR_HEIGHT,
                scr_w,
                grid_bottom
            )
            world.camera_x = cx
            world.camera_y = cy

        if event.type == pygame.MOUSEBUTTONUP:
            minimap_dragging = False

        # --- Toolbar
        if event.type == pygame.MOUSEBUTTONDOWN:
            scroll_offset, world.current_terrain, world.current_brush, used = handle_toolbar_click(
                mouse_pos,
                scroll_offset,
                scr_w,
                grid_bottom,
                TOOLBAR_BUTTONS,
                world.current_terrain,
                world.current_brush
            )
            if used:
                continue

        # --- Dessin
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # clic gauche = dessin
                is_drawing = True
                # Convertir la position souris en coordonnées grille
                mx, my = mouse_pos
                # Ajuster selon caméra et taille des tuiles
                col = int((mx + world.camera_x) // world.tile_size)
                row = int((my + world.camera_y) // world.tile_size)
                world.paint(row, col)

            elif event.button == 3:  # clic droit = début pan
                is_panning = True
                last_mouse = mouse_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_drawing = False
            elif event.button == 3:
                is_panning = False

        elif event.type == pygame.MOUSEMOTION:
            if is_drawing:
                mx, my = mouse_pos
                col = int((mx + world.camera_x) // world.tile_size)
                row = int((my + world.camera_y) // world.tile_size)
                world.paint(row, col)

            if is_panning:
                mx, my = mouse_pos
                dx = last_mouse[0] - mx
                dy = last_mouse[1] - my

                world.camera_x = max(0, min(world.camera_x + dx, GRID_WIDTH * world.tile_size - scr_w))
                world.camera_y = max(0, min(world.camera_y + dy, GRID_HEIGHT * world.tile_size - grid_bottom))

                last_mouse = mouse_pos

    # -------------------------------------
    #               RENDER
    # -------------------------------------

    screen.fill((0, 0, 0))

    if APP_STATE == "START":
        START_BUTTONS = draw_start_screen(
            screen,
            scr_w,
            scr_h,
            font,
            title_font
        )
    else:
        draw_world(screen, world, scaled_assets)
        draw_toolbar(
            screen,
            world,
            scroll_offset,
            scr_w,
            grid_bottom,
            font,
            TOOLBAR_BUTTONS,
            COLORS,
            world.current_terrain,
            world.current_brush
        )

        draw_minimap(
            screen,
            world.grid,
            world.camera_x,
            world.camera_y,
            scr_w,
            grid_bottom,
            world.tile_size,
            COLORS
        )

    pygame.display.flip()
    clock.tick(60)
